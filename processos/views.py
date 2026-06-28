from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q
from datetime import date
from .models import LogSistema, Processo, AndamentoProcesso, Cliente, Advogado, Juiz, Forum
from .forms import ProcessoForm, ClienteForm, AdvogadoForm, JuizForm, ForumForm, UsuarioForm


@login_required
def cadastrar_processo(request):
    if request.method == 'POST':
        form = ProcessoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProcessoForm()
    return render(request, 'processos/cadastro_processo.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    erro = None
    if request.method == 'POST':
        usuario_digitado = request.POST.get('usuario')
        senha_digitada = request.POST.get('senha')
        usuario = authenticate(request, username=usuario_digitado, password=senha_digitada)
        if usuario is not None:
            login(request, usuario)
            LogSistema.objects.create(
                usuario=usuario,
                acao='LOGIN',
                descricao=f"Usuário {usuario.username} entrou no sistema com sucesso."
            )
            return redirect('dashboard')
        else:
            erro = "Usuário ou senha incorretos. Tente novamente."
    return render(request, 'processos/login.html', {'erro': erro})


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'processos/dashboard.html')


@login_required(login_url='login')
def buscar_processos_view(request):
    estatisticas = Processo.objects.aggregate(
        total=Count('id'),
        ativos=Count('id', filter=Q(status='ativo')),
        substabelecidos=Count('id', filter=Q(status='substabelecido')),
        desistencias=Count('id', filter=Q(status='desistencia')),
        arquivados=Count('id', filter=Q(status='arquivado'))
    )
    processos = Processo.objects.all().select_related('cliente', 'advogado', 'juiz', 'forum')
    filtro_numero = request.GET.get('busca_numero')
    filtro_cliente = request.GET.get('busca_cliente')
    filtro_advogado = request.GET.get('busca_advogado')
    filtro_status = request.GET.get('busca_status')
    veio_do_detalhe = request.META.get('HTTP_REFERER') and 'detalhe' in request.META.get('HTTP_REFERER', '')
    if not (filtro_numero or filtro_cliente or filtro_advogado or filtro_status) and veio_do_detalhe:
        filtro_numero = request.session.get('filtro_proc_numero', '')
        filtro_cliente = request.session.get('filtro_proc_cliente', '')
        filtro_advogado = request.session.get('filtro_proc_advogado', '')
        filtro_status = request.session.get('filtro_proc_status', '')
    else:
        request.session['filtro_proc_numero'] = filtro_numero or ''
        request.session['filtro_proc_cliente'] = filtro_cliente or ''
        request.session['filtro_proc_advogado'] = filtro_advogado or ''
        request.session['filtro_proc_status'] = filtro_status or ''
    termos_pesquisados = []
    if filtro_numero:
        processos = processos.filter(numero_processo__icontains=filtro_numero)
        termos_pesquisados.append(f"Número: '{filtro_numero}'")
    if filtro_cliente:
        processos = processos.filter(cliente__nome__icontains=filtro_cliente)
        termos_pesquisados.append(f"Cliente: '{filtro_cliente}'")
    if filtro_advogado:
        processos = processos.filter(advogado__nome__icontains=filtro_advogado)
        termos_pesquisados.append(f"Advogado: '{filtro_advogado}'")
    if filtro_status:
        processos = processos.filter(status__iexact=filtro_status.strip())
        termos_pesquisados.append(f"Status: '{filtro_status}'")
    if termos_pesquisados and request.GET:
        descricao_log = f"Usuário buscou processos usando os critérios -> {', '.join(termos_pesquisados)}."
        LogSistema.objects.create(usuario=request.user, acao='BUSCA', descricao=descricao_log)
    contexto = {
        'processos': processos,
        'estatisticas': estatisticas,
        'valores_filtros': {
            'numero': filtro_numero,
            'cliente': filtro_cliente,
            'advogado': filtro_advogado,
            'status': filtro_status,
        }
    }
    return render(request, 'processos/buscar_processos.html', contexto)


def logout_view(request):
    if request.user.is_authenticated:
        LogSistema.objects.create(
            usuario=request.user,
            acao='LOGIN',
            descricao=f"Usuário {request.user.username} saiu do sistema (Logout)."
        )
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def detalhe_processo_view(request, processo_id):
    processo = get_object_or_404(Processo.objects.select_related('cliente', 'advogado', 'juiz', 'forum'), id=processo_id)
    if request.method == 'POST' and 'salvar_andamento' in request.POST:
        data_evento = request.POST.get('data_evento')
        descricao_evento = request.POST.get('descricao_evento')
        if data_evento and descricao_evento:
            AndamentoProcesso.objects.create(
                processo=processo, data=data_evento, descricao=descricao_evento.strip()
            )
            LogSistema.objects.create(
                usuario=request.user, acao='VISUALIZACAO',
                descricao=f"Usuário registrou um novo andamento no Processo Nº {processo.numero_processo}."
            )
            return redirect('detalhe_processo', processo_id=processo.id)
    andamentos = processo.andamentos.all()
    if request.method == 'GET':
        LogSistema.objects.create(
            usuario=request.user, acao='VISUALIZACAO',
            descricao=f"Usuário visualizou os detalhes do Processo Nº {processo.numero_processo}."
        )
    contexto = {
        'processo': processo,
        'andamentos': andamentos,
        'data_hoje': date.today().strftime('%Y-%m-%d')
    }
    return render(request, 'processos/detalhe_processo.html', contexto)


@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': cliente.id, 'nome': cliente.nome})
            return redirect('dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                erros_limpos = {campo: mensagens[0] for campo, mensagens in form.errors.items()}
                return JsonResponse({'success': False, 'errors': erros_limpos}, status=400)
    else:
        form = ClienteForm()
    return render(request, 'processos/cadastro_cliente.html', {'form': form})


@login_required
def cadastrar_advogado(request):
    if request.method == 'POST':
        form = AdvogadoForm(request.POST)
        if form.is_valid():
            advogado = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': advogado.id, 'nome': advogado.nome})
            return redirect('dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                erros_limpos = {campo: mensagens[0] for campo, mensagens in form.errors.items()}
                return JsonResponse({'success': False, 'errors': erros_limpos}, status=400)
    else:
        form = AdvogadoForm()
    return render(request, 'processos/cadastro_advogado.html', {'form': form})


@login_required(login_url='login')
def painel_analitico_view(request):
    dados_status = Processo.objects.aggregate(
        ativos=Count('id', filter=Q(status='ativo')),
        encerrados=Count('id', filter=Q(status='encerrado')),
        substabelecidos=Count('id', filter=Q(status='substabelecido')),
        desistencias=Count('id', filter=Q(status='desistencia')),
        arquivados=Count('id', filter=Q(status='arquivado'))
    )
    contexto = {'dados_status': dados_status}
    return render(request, 'processos/painel_analitico.html', contexto)


# --- NOVAS VIEWS DE CADASTRO ---

@login_required
def cadastrar_juiz(request):
    if request.method == 'POST':
        form = JuizForm(request.POST)
        if form.is_valid():
            juiz = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': juiz.id, 'nome': juiz.nome})
            return redirect('dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                erros_limpos = {campo: mensagens[0] for campo, mensagens in form.errors.items()}
                return JsonResponse({'success': False, 'errors': erros_limpos}, status=400)
    else:
        form = JuizForm()
    return render(request, 'processos/cadastro_juiz.html', {'form': form})


@login_required
def cadastrar_forum(request):
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': forum.id, 'nome': forum.nome})
            return redirect('dashboard')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                erros_limpos = {campo: mensagens[0] for campo, mensagens in form.errors.items()}
                return JsonResponse({'success': False, 'errors': erros_limpos}, status=400)
    else:
        form = ForumForm()
    return render(request, 'processos/cadastro_forum.html', {'form': form})


# --- GESTÃO DE USUÁRIOS ---

@login_required
def gerenciar_usuarios(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    usuarios = User.objects.all().order_by('-date_joined')
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'processos/gerenciar_usuarios.html', {'usuarios': usuarios, 'form': form})


@login_required
def desativar_usuario(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')
    usuario = get_object_or_404(User, id=user_id)
    if usuario != request.user:
        usuario.is_active = not usuario.is_active
        usuario.save()
    return redirect('gerenciar_usuarios')


# --- RELATÓRIOS ---

@login_required(login_url='login')
def relatorio_por_cliente(request):
    clientes = Cliente.objects.filter(ativo=True).annotate(
        total_processos=Count('processo'),
        processos_ativos=Count('processo', filter=Q(processo__status='ativo'))
    ).order_by('nome')
    return render(request, 'processos/relatorio_clientes.html', {'clientes': clientes})


@login_required(login_url='login')
def relatorio_detalhe_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    processos = Processo.objects.filter(cliente=cliente).select_related('advogado', 'juiz', 'forum')
    return render(request, 'processos/relatorio_detalhe_cliente.html', {
        'cliente': cliente,
        'processos': processos,
        'total': processos.count(),
        'ativos': processos.filter(status='ativo').count()
    })


@login_required(login_url='login')
def relatorio_por_advogado(request):
    advogados = Advogado.objects.filter(ativo=True).annotate(
        total_processos=Count('processo'),
        processos_ativos=Count('processo', filter=Q(processo__status='ativo'))
    ).order_by('nome')
    return render(request, 'processos/relatorio_advogados.html', {'advogados': advogados})


@login_required(login_url='login')
def relatorio_detalhe_advogado(request, advogado_id):
    advogado = get_object_or_404(Advogado, id=advogado_id)
    processos = Processo.objects.filter(advogado=advogado).select_related('cliente', 'juiz', 'forum')
    return render(request, 'processos/relatorio_detalhe_advogado.html', {
        'advogado': advogado,
        'processos': processos,
        'total': processos.count(),
        'ativos': processos.filter(status='ativo').count()
    })


@login_required(login_url='login')
def relatorio_por_juiz(request):
    juizes = Juiz.objects.filter(ativo=True).annotate(
        total_processos=Count('processo'),
        processos_ativos=Count('processo', filter=Q(processo__status='ativo'))
    ).order_by('nome')
    return render(request, 'processos/relatorio_juizes.html', {'juizes': juizes})


@login_required(login_url='login')
def relatorio_detalhe_juiz(request, juiz_id):
    juiz = get_object_or_404(Juiz, id=juiz_id)
    processos = Processo.objects.filter(juiz=juiz).select_related('cliente', 'advogado', 'forum')
    return render(request, 'processos/relatorio_detalhe_juiz.html', {
        'juiz': juiz,
        'processos': processos,
        'total': processos.count(),
        'ativos': processos.filter(status='ativo').count()
    })
