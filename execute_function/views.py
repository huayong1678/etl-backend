from django.shortcuts import render
from logging import raiseExceptions
import datetime
import json
import boto3
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from db_handler.dynamoDB import *
from jwt_authentication.jwtAuth import *
from db_handler.dynamoDB import *
from db_handler.dbTable import *
from database_migration.dms import *
from transforms.serializers import TransformSerializer
from transforms.models import Transform
from pipelines.serializers import PipelineSerializer
from pipelines.models import Pipeline
from dests.serializers import DestSerializer
from dests.models import Dest
from sources.serializers import SourceSerializer
from sources.models import Source
from django.http import HttpResponseServerError


class PrepareTableView(APIView):
    def get(self, request, pipeline_pk, transform_pk):
        token = request.COOKIES.get('jwt')
        payload = isAuthen(token)
        try:
            transform = Transform.objects.filter(
                owner_id=payload['id']).get(pk=transform_pk)
            transform_serializer = TransformSerializer(transform)
            pipeline = Pipeline.objects.filter(
                owner_id=payload['id']).get(pk=pipeline_pk)
            pipeline_serializer = PipelineSerializer(pipeline)
            dest = Dest.objects.filter(owner_id=payload['id']).get(
                pk=pipeline_serializer.data['dest'])
            dest_serializer = DestSerializer(dest)
            database = dest_serializer.data['database']
            db_engine = dest_serializer.data['engine']
            user = dest_serializer.data['user']
            password = dest_serializer.data['password']
            host = dest_serializer.data['host']
            table = dest_serializer.data['tablename']
            port = dest_serializer.data['port']
            isSensitive = pipeline_serializer.data['isSensitive']
            connection_data = [db_engine, user, password,
                               host, database, isSensitive, table, port]
            dynamo_response = dynamoGetTransform(transform_serializer.data)
            # print(dynamo_response)
            schema = getSchema(connection_data)
            # print(schema)
            # head = showData(connection_data)
            # print(head)
        except:
            raise Http404
        # transform_data = {
        #     "schemas": dynamo_response['Item']['SCHEMAS'], "scripts": dynamo_response['Item']['SCRIPTS']}
        transform_data = {
            "schemas": dynamo_response['Item']['SCHEMAS']}
        dest_data = {"schemas": schema if schema != table else "unavailable"}
        if checkTable(connection_data)['status'] == False:
            response = {"detail": "no such table", "source_schema" if schema !=
                        table else "required_source_table": schema, "transform_data": transform_data, "dest_data": dest_data}
        else:
            response = {"detail": "available", "source_schema" if schema !=
                        table else "required_table": schema, "transform_data": transform_data, "dest_data": dest_data}
        return Response(response)


class ApplyTableView(APIView):
    def post(self, request, pipeline_pk, transform_pk):
        token = request.COOKIES.get('jwt')
        payload = isAuthen(token)
        try:
            transform = Transform.objects.filter(
                owner_id=payload['id']).get(pk=transform_pk)
            transform_serializer = TransformSerializer(transform)
            pipeline = Pipeline.objects.filter(
                owner_id=payload['id']).get(pk=pipeline_pk)
            pipeline_serializer = PipelineSerializer(pipeline)
            dest = Dest.objects.filter(owner_id=payload['id']).get(
                pk=pipeline_serializer.data['dest'])
            dest_serializer = DestSerializer(dest)
            database = dest_serializer.data['database']
            db_engine = dest_serializer.data['engine']
            user = dest_serializer.data['user']
            password = dest_serializer.data['password']
            host = dest_serializer.data['host']
            table = dest_serializer.data['tablename']
            port = dest_serializer.data['port']
            isSensitive = pipeline_serializer.data['isSensitive']
            connection_data = [db_engine, user, password,
                               host, database, isSensitive, table, port]
            try:
                dynamo_response = dynamoGetTransform(transform_serializer.data)
                print(dynamo_response['Item']['SCHEMAS'])
                if request.data['create_table']:
                    create_status = createTable(connection_data,
                                                dynamo_response['Item']['SCHEMAS'], request.data['pk'])
                    table_status = checkTable(connection_data)
                    response = {
                        "table_name": table, "schemas_to_apply": dynamo_response['Item']['SCHEMAS'], "detail": create_status}
                else:
                    response = {
                        "detail": "Execution Cancled. Any change will not apply."}
            except:
                return HttpResponseServerError()
        except:
            raise Http404
        return Response(response)


class ApplyMigrateView(APIView):
    def get(self, request, pipeline_pk, transform_pk):
        token = request.COOKIES.get('jwt')
        payload = isAuthen(token)
        try:
            pipeline = Pipeline.objects.filter(
                owner_id=payload['id']).get(pk=pipeline_pk)
            pipeline_serializer = PipelineSerializer(pipeline)
            source = Source.objects.filter(owner_id=payload['id']).get(
                pk=pipeline_serializer.data['source'])
            source_serializer = SourceSerializer(source)
            transform = Transform.objects.filter(
                owner_id=payload['id']).get(pk=transform_pk)
            transform_serializer = TransformSerializer(transform)
            database = source_serializer.data['database']
            db_engine = source_serializer.data['engine']
            user = source_serializer.data['user']
            password = source_serializer.data['password']
            host = source_serializer.data['host']
            table = source_serializer.data['tablename']
            port = source_serializer.data['port']
            connection_data = [db_engine, user, password,
                               host, database, 0, table, port]
            # connection_data = [db_engine, user, password,
            #                 host, port, database, table]
            try:
                response = dynamoGetTransform(transform_serializer.data)
                dest = Dest.objects.filter(owner_id=payload['id']).get(
                    pk=pipeline_serializer.data['dest'])
                dest_serializer = DestSerializer(dest)
                database = dest_serializer.data['database']
                db_engine = dest_serializer.data['engine']
                user = dest_serializer.data['user']
                password = dest_serializer.data['password']
                host = dest_serializer.data['host']
                table = dest_serializer.data['tablename']
                port = dest_serializer.data['port']
                dest_connection_data = [db_engine, user, password,
                                        host, database, 0, table, port]
                exp = exportData(connection_data, payload['id'], response)
                print(exp)
                upload = multi_part_upload_with_s3(
                    exp[1], exp[2], payload['id'])
                print(upload)
                imp = importData(dest_connection_data, exp[1], response)
                rmv = removeLocalData(exp[1])
            except:
                return HttpResponseServerError()
        except:
            raise Http404
        return Response({"export": exp[-1], "upload": upload, "import": imp, "remove": rmv})
