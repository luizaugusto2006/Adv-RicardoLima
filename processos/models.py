from django.db import models
from django.contrib.auth.models import User


class Advogado(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Advogado")
    oab = models.CharField(max_length=20, verbose_name="Inscrição OAB", unique=True)
    email = models.EmailField(blank=True, null=True)
    ativo = models.BooleanField(default=True, verbose_name="Cadastro Ativo")

    def __str__(self):
        return f"{self.nome} (OAB: {self.oab})"


class Cliente(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Cliente")
    cpf = models.CharField(max_length=14, verbose_name="CPF", unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    ativo = models.BooleanField(default=True, verbose_name="Cadastro Ativo")

    def __str__(self):
        return self.nome


class Forum(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Fórum")
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    uf = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Fórum"
        verbose_name_plural = "Fóruns"

    def __str__(self):
        return self.nome


class Juiz(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Juiz")
    email = models.EmailField(blank=True, null=True)
    forum = models.ForeignKey(Forum, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Fórum Vinculado")
    ativo = models.BooleanField(default=True, verbose_name="Cadastro Ativo")

    class Meta:
        verbose_name = "Juiz"
        verbose_name_plural = "Juízes"

    def __str__(self):
        return self.nome


class Processo(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Em Andamento / Ativo'),
        ('encerrado', 'Encerrado / Julgado'),
        ('substabelecido', 'Substabelecido (Outro Escritório)'),
        ('desistencia', 'Desistência pelo Cliente'),
        ('arquivado', 'Arquivado'),
    ]

    numero_processo = models.CharField(max_length=50, unique=True, verbose_name="Número do Processo")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    advogado = models.ForeignKey(Advogado, on_delete=models.PROTECT, verbose_name="Advogado Responsável")
    juiz = models.ForeignKey(Juiz, on_delete=models.PROTECT, verbose_name="Juiz Responsável")
    forum = models.ForeignKey(Forum, on_delete=models.PROTECT, verbose_name="Fórum", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name="Status do Processo")
    resumo_sentenca = models.TextField(verbose_name="Resumo da Causa / Sentença", blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proc. Nº {self.numero_processo} - {self.cliente.nome}"


class HistoricoProcesso(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name="historicos")
    data_atualizacao = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(verbose_name="Histórico / Movimentação")

    def __str__(self):
        return f"Atualização do processo {self.processo.numero_processo} em {self.data_atualizacao.strftime('%d/%m/%Y')}"


class LogSistema(models.Model):
    AÇÕES = [
        ('LOGIN', 'Login no Sistema'),
        ('BUSCA', 'Realizou Pesquisa'),
        ('VISUALIZACAO', 'Visualizou Processo'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    acao = models.CharField(max_length=20, choices=AÇÕES, verbose_name="Ação")
    descricao = models.TextField(verbose_name="Descrição da Atividade")
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    class Meta:
        verbose_name = "Log do Sistema"
        verbose_name_plural = "Logs do Sistema"

    def __str__(self):
        return f"{self.usuario.username} - {self.get_acao_display()} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class AndamentoProcesso(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='andamentos', verbose_name="Processo")
    data = models.DateField(verbose_name="Data do Evento")
    descricao = models.TextField(verbose_name="Descrição do Andamento")

    class Meta:
        verbose_name = "Andamento do Processo"
        verbose_name_plural = "Andamentos do Processo"
        ordering = ['-data']

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} - {self.processo.numero_processo}"