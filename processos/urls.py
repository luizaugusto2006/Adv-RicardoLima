from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('processo/buscar/', views.buscar_processos_view, name='buscar_processos'),
    path('processo/novo/', views.cadastrar_processo, name='cadastrar_processo'),
    path('processo/<int:processo_id>/', views.detalhe_processo_view, name='detalhe_processo'),
    path('clientes/novo/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('advogados/novo/', views.cadastrar_advogado, name='cadastrar_advogado'),
    path('juizes/novo/', views.cadastrar_juiz, name='cadastrar_juiz'),
    path('foruns/novo/', views.cadastrar_forum, name='cadastrar_forum'),
    path('logout/', views.logout_view, name='logout'),
    path('painel-analitico/', views.painel_analitico_view, name='painel_analitico'),

    # Gestão de Usuários
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('usuarios/<int:user_id>/desativar/', views.desativar_usuario, name='desativar_usuario'),

    # Relatórios
    path('relatorios/clientes/', views.relatorio_por_cliente, name='relatorio_clientes'),
    path('relatorios/clientes/<int:cliente_id>/', views.relatorio_detalhe_cliente, name='relatorio_detalhe_cliente'),
    path('relatorios/advogados/', views.relatorio_por_advogado, name='relatorio_advogados'),
    path('relatorios/advogados/<int:advogado_id>/', views.relatorio_detalhe_advogado, name='relatorio_detalhe_advogado'),
    path('relatorios/juizes/', views.relatorio_por_juiz, name='relatorio_juizes'),
    path('relatorios/juizes/<int:juiz_id>/', views.relatorio_detalhe_juiz, name='relatorio_detalhe_juiz'),
]
