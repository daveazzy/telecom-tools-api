#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados.
Use para diagnosticar problemas de conexão antes do deploy.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings


def test_database_connection():
    """Testa a conexão com o banco de dados."""
    
    print("=" * 60)
    print("🔍 Teste de Conexão com Banco de Dados")
    print("=" * 60)
    print()
    
    # Informações de configuração
    print("📊 Configuração:")
    print(f"  Ambiente: {settings.ENVIRONMENT}")
    print(f"  Database URL: {settings.DATABASE_URL[:50]}...")
    
    db_type = "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite"
    print(f"  Tipo de Banco: {db_type}")
    print()
    
    # Testar conexão
    print("🔌 Testando conexão...")
    
    try:
        # Preparar connect_args
        connect_args = {}
        if "sqlite" in settings.DATABASE_URL:
            connect_args = {"check_same_thread": False}
        elif "postgresql" in settings.DATABASE_URL:
            connect_args = {
                "connect_timeout": 10,
                "options": "-c statement_timeout=30000"
            }
        
        # Criar engine
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=False,
            connect_args=connect_args
        )
        
        # Tentar conectar
        with engine.connect() as connection:
            print("  ✅ Conexão estabelecida com sucesso!")
            print()
            
            # Executar query de teste
            print("🧪 Executando query de teste...")
            result = connection.execute(text("SELECT 1"))
            print(f"  ✅ Query executada com sucesso: {result.scalar()}")
            print()
            
            # Informações adicionais para PostgreSQL
            if "postgresql" in settings.DATABASE_URL:
                print("📈 Informações do PostgreSQL:")
                
                # Versão
                result = connection.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"  Versão: {version.split(',')[0]}")
                
                # Database name
                result = connection.execute(text("SELECT current_database()"))
                db_name = result.scalar()
                print(f"  Database: {db_name}")
                
                # User
                result = connection.execute(text("SELECT current_user"))
                user = result.scalar()
                print(f"  Usuário: {user}")
                
                # Número de conexões
                result = connection.execute(text(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                ))
                connections = result.scalar()
                print(f"  Conexões ativas: {connections}")
                print()
        
        # Testar criação de tabelas
        print("🏗️  Testando criação de tabelas...")
        from app.core.database import Base
        Base.metadata.create_all(bind=engine)
        print("  ✅ Tabelas criadas/verificadas com sucesso!")
        print()
        
        # Listar tabelas criadas
        print("📋 Tabelas no banco:")
        if "postgresql" in settings.DATABASE_URL:
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
                ))
                tables = result.fetchall()
                if tables:
                    for table in tables:
                        print(f"  • {table[0]}")
                else:
                    print("  (nenhuma tabela encontrada)")
        else:
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ))
                tables = result.fetchall()
                if tables:
                    for table in tables:
                        print(f"  • {table[0]}")
                else:
                    print("  (nenhuma tabela encontrada)")
        
        print()
        print("=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print()
        print("💡 Dica: Se este teste passou, sua configuração está correta.")
        print("   O deploy no Railway deve funcionar sem problemas.")
        print()
        
        return True
        
    except Exception as e:
        print("  ❌ ERRO na conexão!")
        print()
        print("=" * 60)
        print("❌ ERRO DETECTADO")
        print("=" * 60)
        print()
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print()
        
        # Dicas de troubleshooting
        print("🔧 Troubleshooting:")
        print()
        
        if "could not connect to server" in str(e).lower():
            print("  • O servidor PostgreSQL não está acessível")
            print("  • Verifique se o host e porta estão corretos")
            print("  • Verifique se o PostgreSQL está rodando")
            print("  • Verifique as regras de firewall")
            
        elif "password authentication failed" in str(e).lower():
            print("  • Credenciais incorretas")
            print("  • Verifique usuário e senha na DATABASE_URL")
            
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            print("  • O banco de dados especificado não existe")
            print("  • Crie o banco ou verifique o nome na DATABASE_URL")
            
        elif "psycopg2" in str(e).lower():
            print("  • Driver PostgreSQL não instalado corretamente")
            print("  • Execute: pip install psycopg2-binary")
            
        else:
            print("  • Verifique a DATABASE_URL no arquivo .env")
            print("  • Confirme que todas as dependências estão instaladas")
            print("  • Execute: pip install -r requirements.txt")
        
        print()
        print(f"DATABASE_URL atual: {settings.DATABASE_URL[:50]}...")
        print()
        
        return False


if __name__ == "__main__":
    try:
        success = test_database_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


