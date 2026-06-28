from django.core.management.base import BaseCommand
from processos.models import Cliente 

class Command(BaseCommand):
    help = 'Remove caracteres não numéricos dos CPFs de todos os clientes cadastrados'

    def handle(self, *args, **kwargs):
        # Busca todos os clientes
        clientes = Cliente.objects.all()
        contagem = 0
        
        self.stdout.write("Iniciando limpeza de CPFs...")

        for cliente in clientes:
            if cliente.cpf:
                # Remove tudo que não é número (mantém apenas 0-9)
                novo_cpf = ''.join(filter(str.isdigit, cliente.cpf))
                
                # Se o valor mudou (tinha letra ou traço/ponto), salva o novo formato
                if novo_cpf != cliente.cpf:
                    cliente.cpf = novo_cpf
                    cliente.save()
                    contagem += 1
        
        self.stdout.write(self.style.SUCCESS(f'Limpeza concluída! {contagem} registros foram corrigidos.'))