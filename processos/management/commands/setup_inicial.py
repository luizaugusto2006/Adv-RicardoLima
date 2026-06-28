from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from processos.models import Advogado, Cliente, Forum, Juiz
import getpass


class Command(BaseCommand):
    help = "Configuração inicial do sistema: cria superuser e dados básicos"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.WARNING("   CONFIGURAÇÃO INICIAL - RICARDO LIMA ADVOGADOS"))
        self.stdout.write(self.style.WARNING("=" * 60))

        # Criar superuser
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write("\nCriando superusuário...")
            username = input("Username (admin): ") or "admin"
            email = input("Email (admin@example.com): ") or "admin@example.com"
            senha = getpass.getpass("Senha: ")
            if not senha:
                senha = "admin123"
            User.objects.create_superuser(username=username, email=email, password=senha)
            self.stdout.write(self.style.SUCCESS(f"Superusuário '{username}' criado!"))
        else:
            self.stdout.write("Superusuário já existe. Pulando.")

        # Criar fóruns padrão
        if not Forum.objects.exists():
            self.stdout.write("\nCriando fóruns padrão...")
            foruns = [
                {"nome": "Fórum Trabalhista de São Paulo", "cidade": "São Paulo", "uf": "SP"},
                {"nome": "Fórum Trabalhista de Campinas", "cidade": "Campinas", "uf": "SP"},
                {"nome": "Fórum Trabalhista de Santos", "cidade": "Santos", "uf": "SP"},
            ]
            for f in foruns:
                Forum.objects.create(**f)
            self.stdout.write(self.style.SUCCESS(f"{len(foruns)} fóruns criados!"))
        else:
            self.stdout.write("Fóruns já existem. Pulando.")

        # Criar juízes padrão
        if not Juiz.objects.exists():
            self.stdout.write("\nCriando juízes padrão...")
            forum_sp = Forum.objects.filter(cidade="São Paulo").first()
            Juiz.objects.create(nome="Dr. Carlos Alberto Mendes", forum=forum_sp)
            Juiz.objects.create(nome="Dra. Ana Paula Silveira", forum=forum_sp)
            self.stdout.write(self.style.SUCCESS("Juízes criados!"))
        else:
            self.stdout.write("Juízes já existem. Pulando.")

        # Criar advogados padrão
        if not Advogado.objects.exists():
            self.stdout.write("\nCriando advogados padrão...")
            Advogado.objects.create(nome="Ricardo Lima", oab="123.456", email="ricardo@example.com")
            Advogado.objects.create(nome="Dra. Mariana Costa", oab="789.012", email="mariana@example.com")
            self.stdout.write(self.style.SUCCESS("Advogados criados!"))
        else:
            self.stdout.write("Advogados já existem. Pulando.")

        # Criar clientes padrão
        if not Cliente.objects.exists():
            self.stdout.write("\nCriando clientes padrão...")
            Cliente.objects.create(nome="Empresa ABC Ltda", cpf="11.222.333/0001-00", telefone="(11) 99999-8888")
            Cliente.objects.create(nome="João da Silva", cpf="111.222.333-44", telefone="(11) 98888-7777")
            self.stdout.write(self.style.SUCCESS("Clientes criados!"))
        else:
            self.stdout.write("Clientes já existem. Pulando.")

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("   CONFIGURAÇÃO INICIAL CONCLUÍDA!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
