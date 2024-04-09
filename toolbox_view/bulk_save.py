import datetime

from django.core.management.color import no_style
from django.db import connection

from toolbox_view.helpers import task_print


class BulkSave:
    bulk_amount = 100

    def __del__(self):
        if self.records:
            self.bulk_save()

    def __init__(self, *, model, store_ids=False, modal_task=None, task_title=None):
        self.record_no = 0
        self.records = []
        self.model = model
        self.ids_added = []
        self.store_ids = store_ids
        self.modal_task = modal_task
        self.task_title = task_title

    def bulk_save(self):
        self.model.objects.bulk_create(self.records)
        if self.store_ids:
            self.ids_added += [r.id for r in self.records]

    def append(self, instance):
        self.records.append(instance)
        if len(self.records) >= self.bulk_amount:
            self.record_no += self.bulk_amount
            self.bulk_save()
            if self.modal_task:
                self.modal_task.update_state(
                    state='PROGRESS', meta={'message': f'{self.task_title}<br>Adding Records - {self.record_no}'}
                )
            else:
                print(f'Adding records - {self.record_no}')
            self.records = []

    def finish(self):
        if self.records:
            self.bulk_save()
            self.records = []


class BulkSaveSQL(BulkSave):

    def __init__(self, *, fields, model, model_id=None, **kwargs):
        self.model_id = model_id
        self.fields = fields
        super().__init__(model=model, **kwargs)

    def bulk_save(self):
        values = []
        for r in self.records:
            field_results = []
            for f in self.fields:
                v = getattr(r, f)
                if v is None:
                    field_results.append('NULL')
                elif isinstance(v, str):
                    v = v.replace("'", "''")
                    field_results.append(f"'{v}'")
                elif isinstance(v, (datetime.date, datetime.datetime)):
                    field_results.append(f"'{v.strftime('%Y-%m-%d')}'")
                else:
                    field_results.append(str(v))
            values.append('(' + ','.join(field_results) + ')')
        # noinspection SqlDialectInspection,PyProtectedMember
        sql = f'INSERT INTO {self.model._meta.db_table} ({", ".join(self.fields)}) VALUES {",".join(values)}'
        if self.model_id:
            sql += f' RETURNING {self.model_id}'
        sql += ';'
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if self.model_id:
                for c, returned_id in enumerate(cursor.fetchall()):
                    self.records[c].id = returned_id[0]


def delete_reset(*models, query_filter=None, raw=False, task_object=None):
    for model in models:
        task_print(task_object, f'Deleting {model.__name__}')
        query_filter = {} if query_filter is None else query_filter
        manager = model.all if hasattr(model, 'all') else model.objects
        if raw:
            # noinspection PyProtectedMember
            manager.all().filter(**query_filter)._raw_delete(model.objects.db)
        else:
            manager.all().filter(**query_filter).delete()
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [model])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
