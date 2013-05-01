# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ObjectLock'
        db.create_table('django_snailtracker_objectlock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('table', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('object_pk', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('django_snailtracker', ['ObjectLock'])

        # Adding unique constraint on 'ObjectLock', fields ['table', 'object_pk']
        db.create_unique('django_snailtracker_objectlock', ['table', 'object_pk'])


    def backwards(self, orm):
        # Removing unique constraint on 'ObjectLock', fields ['table', 'object_pk']
        db.delete_unique('django_snailtracker_objectlock', ['table', 'object_pk'])

        # Deleting model 'ObjectLock'
        db.delete_table('django_snailtracker_objectlock')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_snailtracker.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'columns_changed': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_init_snapshot': ('django.db.models.fields.TextField', [], {}),
            'post_save_snapshot': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'real_event_time': ('django.db.models.fields.DateTimeField', [], {}),
            'snailtrack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_snailtracker.Snailtrack']"}),
            'story': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'django_snailtracker.objectlock': {
            'Meta': {'unique_together': "(('table', 'object_pk'),)", 'object_name': 'ObjectLock'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'table': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_snailtracker.snailtrack': {
            'Meta': {'object_name': 'Snailtrack'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['django_snailtracker.Snailtrack']"})
        }
    }

    complete_apps = ['django_snailtracker']