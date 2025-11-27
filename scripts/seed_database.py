"""Seed database with realistic sample data for demonstration"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.signal_measurement import SignalMeasurement, SignalType
from app.models.tower import Tower
from app.models.speed_test import SpeedTest


def seed_users(db):
    """Create demo users"""
    print("🔑 Criando usuários de demonstração...")
    
    users = [
        {
            "email": "demo@telecom-api.com",
            "username": "demo",
            "full_name": "Usuário Demonstração",
            "password": "demo123456"
        },
        {
            "email": "analista@telecom-api.com",
            "username": "analista",
            "full_name": "Analista de Cobertura",
            "password": "demo123456"
        }
    ]
    
    created_users = []
    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
                is_superuser=False
            )
            db.add(user)
            created_users.append(user)
    
    db.commit()
    print(f"✓ {len(created_users)} usuários criados")
    return created_users


def generate_towers_grid(base_lat, base_lon, grid_size=10, spacing=0.01):
    """Generate a grid of towers with realistic distribution"""
    towers = []
    operators = ["VIVO", "CLARO", "TIM", "OI"]
    technologies = ["4G", "5G", "LTE"]
    frequencies = {
        "4G": [800, 1800, 2100, 2600],
        "5G": [3500, 28000],
        "LTE": [1800, 2100, 2600]
    }
    
    for i in range(grid_size):
        for j in range(grid_size):
            lat = base_lat + (i - grid_size/2) * spacing
            lon = base_lon + (j - grid_size/2) * spacing
            
            operator = random.choice(operators)
            tech = random.choice(technologies)
            freq = random.choice(frequencies[tech])
            
            towers.append({
                "latitude": lat,
                "longitude": lon,
                "operator": operator,
                "cell_id": f"{operator}-{i:03d}-{j:03d}",
                "technology": tech,
                "frequency_mhz": freq
            })
    
    return towers


def seed_towers(db):
    """Create realistic tower network"""
    print("📡 Criando rede de torres...")
    
    # São Paulo region
    sp_center = [-23.5505, -46.6333]
    
    towers = generate_towers_grid(sp_center[0], sp_center[1], grid_size=15, spacing=0.008)
    
    created = 0
    for tower_data in towers:
        existing = db.query(Tower).filter(Tower.cell_id == tower_data["cell_id"]).first()
        if not existing:
            tower = Tower(**tower_data)
            db.add(tower)
            created += 1
    
    db.commit()
    print(f"✓ {created} torres criadas")


def seed_measurements(db, user):
    """Create realistic signal measurements across the region"""
    print("📊 Criando medições de sinal...")
    
    operators = ["VIVO", "CLARO", "TIM", "OI"]
    signal_types = [SignalType.CELLULAR_4G, SignalType.CELLULAR_5G]
    technologies = ["LTE", "4G", "5G"]
    frequencies = [800, 1800, 2100, 2600, 3500, 28000]
    
    base_lat = -23.5505
    base_lon = -46.6333
    
    created = 0
    # Generate realistic measurements across multiple days
    for day_offset in range(7):
        for _ in range(40):
            operator = random.choice(operators)
            
            # Higher signal strength for 5G
            if operator == "VIVO" and random.random() > 0.3:
                signal_dbm = random.uniform(-85, -55)
                signal_quality = random.randint(70, 100)
            else:
                signal_dbm = random.uniform(-105, -60)
                signal_quality = random.randint(30, 90)
            
            measurement = SignalMeasurement(
                user_id=user.id,
                latitude=base_lat + random.uniform(-0.08, 0.08),
                longitude=base_lon + random.uniform(-0.08, 0.08),
                signal_type=random.choice(signal_types),
                operator=operator,
                signal_strength_dbm=signal_dbm,
                signal_quality=signal_quality,
                frequency_mhz=random.choice(frequencies),
                technology=random.choice(technologies),
                measured_at=datetime.utcnow() - timedelta(days=day_offset, hours=random.randint(0, 24))
            )
            db.add(measurement)
            created += 1
    
    db.commit()
    print(f"✓ {created} medições de sinal criadas")


def seed_speed_tests(db, user):
    """Create realistic speed test results"""
    print("🚀 Criando testes de velocidade...")
    
    operators = ["VIVO", "CLARO", "TIM", "OI"]
    
    # Realistic speed profiles for each operator and connection type
    speed_profiles = {
        ("5g", "VIVO"): {"dl": (80, 200), "ul": (30, 80), "ping": (10, 30)},
        ("5g", "CLARO"): {"dl": (60, 150), "ul": (25, 70), "ping": (15, 35)},
        ("4g", "VIVO"): {"dl": (20, 60), "ul": (5, 25), "ping": (20, 50)},
        ("4g", "CLARO"): {"dl": (15, 50), "ul": (4, 20), "ping": (25, 60)},
        ("4g", "TIM"): {"dl": (12, 40), "ul": (3, 15), "ping": (30, 70)},
        ("wifi", "VIVO"): {"dl": (40, 150), "ul": (15, 60), "ping": (5, 20)},
    }
    
    created = 0
    # Generate speed tests across 14 days
    for day_offset in range(14):
        for _ in range(12):
            operator = random.choice(operators)
            connection_type = random.choice(["4g", "5g", "wifi"])
            
            profile_key = (connection_type, operator)
            if profile_key in speed_profiles:
                profile = speed_profiles[profile_key]
                dl = random.uniform(*profile["dl"])
                ul = random.uniform(*profile["ul"])
                ping = random.uniform(*profile["ping"])
            else:
                dl = random.uniform(10, 80)
                ul = random.uniform(5, 30)
                ping = random.uniform(20, 80)
            
            speed_test = SpeedTest(
                user_id=user.id,
                latitude=-23.5505 + random.uniform(-0.06, 0.06),
                longitude=-46.6333 + random.uniform(-0.06, 0.06),
                download_mbps=max(1, dl),
                upload_mbps=max(1, ul),
                ping_ms=max(1, ping),
                jitter_ms=random.uniform(1, 15),
                packet_loss_percent=random.uniform(0, 3) if random.random() > 0.8 else 0,
                connection_type=connection_type,
                isp=operator,
                operator=operator,
                signal_strength_dbm=random.uniform(-95, -60),
                tested_at=datetime.utcnow() - timedelta(days=day_offset, hours=random.randint(0, 24))
            )
            db.add(speed_test)
            created += 1
    
    db.commit()
    print(f"✓ {created} testes de velocidade criados")


def main():
    """Seed database with realistic demonstration data"""
    print("\n" + "="*60)
    print("  🌱 TELECOM API - SEED DATABASE")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # Seed data
        users = seed_users(db)
        seed_towers(db)
        
        if users:
            seed_measurements(db, users[0])
            seed_speed_tests(db, users[0])
        
        print("\n" + "="*60)
        print("✅ Base de dados populada com sucesso!")
        print("="*60)
        print("\n📋 DADOS CRIADOS:")
        print(f"   • Usuários: 2")
        print(f"   • Torres: 225")
        print(f"   • Medições de sinal: 280")
        print(f"   • Testes de velocidade: 168")
        print("\n🔐 CREDENCIAIS DE DEMONSTRAÇÃO:")
        print(f"   Email: demo@telecom-api.com")
        print(f"   Senha: demo123456")
        print("\n💡 Agora você pode:")
        print(f"   1. Fazer login no frontend")
        print(f"   2. Ver as torres no mapa")
        print(f"   3. Analisar comparação de operadoras")
        print(f"   4. Visualizar medições de sinal")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Erro ao popular base de dados: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

