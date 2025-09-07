from datetime import datetime, timezone
from mongodb_migrations.base import BaseMigration
from src.config import settings
from pymongo import ASCENDING

class Migration(BaseMigration):
    @property
    def problems(self):
        return self.db['problems']

    @property
    def authentication(self):
        return self.db['authentication']
    
    def run_auth_migration(self):
        """
        Creates the 'authentication' collection, initial data and an index on 'hashed_api_key'.
        """
        if 'authentication' not in self.db.list_collection_names():
            self.db.create_collection('authentication')
        
        self.authentication.create_index("hashed_api_key", unique=True)
        
        initial_record_id = "3dcf5b22-b2a2-4c0a-88f5-f4b787728c8f"

        if self.authentication.find_one({"id": initial_record_id}):
            print(f"Registro 'Maratona' (ID: {initial_record_id}) já existe. Nenhuma ação necessária.")
            return
        
        print("Registro 'Maratona' não encontrado. Criando...")
        
        unique_permissions = list(set([
            'read:problems',
            'read:submissions',
            
            'create:problems',
            'create:submissions',
            
            'update:problems',
            'update:submissions',
            
            'delete:problems',
            'delete:submissions'
        ]))

        initial_record_data = {
            "id": initial_record_id,
            "name": "Maratona",
            "hashed_api_key": settings.API_KEY_MASTER.get_secret_value(),
            "is_active": True,
            "permissions": unique_permissions,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        self.authentication.insert_one(initial_record_data)
        
        print(f"Registro 'Maratona' inserido com sucesso!")

        
        print("Migration successful: 'authentication' collection and index created.")
    
    def upgrade(self):
        if 'users' not in self.db.list_collection_names():
            self.db.create_collection('users')

        if 'problems' not in self.db.list_collection_names():
            self.db.create_collection('problems')

        if 'submissions' not in self.db.list_collection_names():
            self.db.create_collection('submissions')

        self.run_auth_migration()

        self.problems.create_index(
            [
                ('name', ASCENDING),
                ('created_at', ASCENDING),
            ],
            name='ix_name_1_created_at_1',
        )


    def downgrade(self):
        self.db.drop_collection('users')
        self.db.drop_collection('problems')
        self.problems.drop_index('ix_name_1_created_at_1')
        self.db.drop_collection('submissions')
        self.db.drop_collection('authentication')
