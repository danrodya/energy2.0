from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Проверяет и создает таблицы если их нет в БД'

    def handle(self, *args, **options):
        """Основная функция команды"""
        self.stdout.write(self.style.SUCCESS('Проверка таблиц в БД...'))
        
        tables_to_check = [
            'devices_device',
            'devices_deviceerror',
            'devices_deviceaction',
            'energy_energyconsumption',
            'energy_dailystatistics',
        ]
        
        with connection.cursor() as cursor:
            missing_tables = []
            
            for table_name in tables_to_check:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [table_name])
                
                exists = cursor.fetchone()
                status = "Существует" if exists else "Отсутствует"
                self.stdout.write(f"  {table_name}: {status}")
                
                if not exists:
                    missing_tables.append(table_name)
        
        if missing_tables:
            self.stdout.write(self.style.WARNING(
                f'\nОбнаружены отсутствующие таблицы: {", ".join(missing_tables)}'
            ))
            self.stdout.write(self.style.SUCCESS('\nПрименение миграций...'))
            
            try:
                call_command('migrate', verbosity=1)
                self.stdout.write(self.style.SUCCESS('\nВсе таблицы успешно созданы!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\nОшибка: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('\nВсе таблицы уже существуют!'))
