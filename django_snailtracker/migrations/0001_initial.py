# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Snailtrack'
        db.create_table('django_snailtracker_snailtrack', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['django_snailtracker.Snailtrack'])),
        ))
        db.send_create_signal('django_snailtracker', ['Snailtrack'])

        # Adding model 'Action'
        db.create_table('django_snailtracker_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snailtrack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_snailtracker.Snailtrack'])),
            ('action_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('real_event_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('columns_changed', self.gf('django.db.models.fields.TextField')(null=True)),
            ('post_init_snapshot', self.gf('django.db.models.fields.TextField')()),
            ('post_save_snapshot', self.gf('django.db.models.fields.TextField')(null=True)),
            ('story', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('django_snailtracker', ['Action'])


    def backwards(self, orm):
        # Deleting model 'Snailtrack'
        db.delete_table('django_snailtracker_snailtrack')

        # Deleting model 'Action'
        db.delete_table('django_snailtracker_action')


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
        'django_snailtracker.snailtrack': {
            'Meta': {'object_name': 'Snailtrack'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['django_snailtracker.Snailtrack']"})
        }
    }

    complete_apps = ['django_snailtracker']