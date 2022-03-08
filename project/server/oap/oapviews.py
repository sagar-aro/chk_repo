# project/server/oap/opaviews.py

import json

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from sqlalchemy import text

from project.notification.oap_email_notofier import EmailNotifier
from project.server import db
from project.server.apputil import AppUtil
from project.server.models import Controller, AlchemyEncoder, Platform, ManualProvisionMaster, ManualProvision, User


class SUTStatusForControllerAPI(MethodView):
    def get(self):
        data = request.args
        controller = data['controller']
        try:
            results = db.session.query(ManualProvision).filter((ManualProvision.is_ifwi == 'In Progress') |
                                                               (ManualProvision.is_ifwi == 'Blocked') |
                                                               (ManualProvision.is_bios == 'In Progress') |
                                                               (ManualProvision.is_bios == 'Blocked') |
                                                               (ManualProvision.is_os == 'In Progress') |
                                                               (ManualProvision.is_os == 'Blocked')).all()
            print(type(results))
            list_data = []
            filter_results = []
            for _val in results:
                if _val.controller == controller:
                    filter_results.append({'controller': _val.controller, 'sut': _val.sut, 'ifwi_status': _val.is_ifwi
                                              , 'bios_status': _val.is_bios, 'os_status': _val.is_os})

            responseObject = {
                'status': 'success',
                'result': filter_results
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            responseObject = {
                'status': 'fail'
            }
            return make_response(jsonify(responseObject)), 500


class OapProvisionAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        try:
            util = AppUtil(list_obj=post_data)
            provision_objects = util.prepareObject()

            db.session.add_all(provision_objects)
            db.session.commit()
            responseObject = {
                'status': 'success',
                'message': 'Successfully Added provision.'
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Add provision.'
            }
            return make_response(jsonify(responseObject)), 500

    def get(self):
        _type = request.args.get('type', None)
        if _type == 'new':
            try:
                results = []
                for m in db.session.query(ManualProvision).all():
                    results.append(
                        {'provision_id': m.provision_id, 'controller': m.controller, 'sut': m.sut, 'is_ifwi': m.is_ifwi,
                         'tws_result_ifwi': m.tws_result_ifwi, 'is_bios': m.is_bios,
                         'tws_result_bios': m.tws_result_bios,
                         'is_os': m.is_os, 'tws_result_os': m.tws_result_os, 'request_id': m.request_id,
                         'user_id': m.user_id,
                         'create_At': m.create_At, 'location_type': m.location_type, 'wwid': m.wwid,
                         'external_id': m.external_id, 'email': m.email,
                         'kit_name': m.kit, 'ifwi_bin': m.ifwi,
                         'wim_name': m.wim_name, 'bios_file': m.bios_file})

                responseObject = {
                    'status': 'success',
                    'data': results
                }
                return make_response(jsonify(responseObject)), 200
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Unable to Fetch provision.',
                    'description': e
                }
                return make_response(jsonify(responseObject)), 500
        else:
            try:
                results = []
                for u, m in db.session.query(User, ManualProvision).filter(User.wwid == ManualProvision.wwid).all():
                    results.append(
                        {'provision_id': m.provision_id, 'controller': m.controller, 'sut': m.sut, 'is_ifwi': m.is_ifwi,
                         'tws_result_ifwi': m.tws_result_ifwi, 'is_bios': m.is_bios,
                         'tws_result_bios': m.tws_result_bios,
                         'is_os': m.is_os, 'tws_result_os': m.tws_result_os, 'request_id': m.request_id,
                         'user_id': m.user_id,
                         'create_At': m.create_At, 'location_type': m.location_type, 'user_name': u.user_name,
                         'email': u.email,
                         'first_name': u.first_name, 'user_group': u.user_group, 'wwid': u.wwid,
                         'last_name': u.last_name})

                responseObject = {
                    'status': 'success',
                    'data': results
                }
                return make_response(jsonify(responseObject)), 200
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Unable to Fetch provision.',
                    'description': e
                }
                return make_response(jsonify(responseObject)), 500

    def patch(self):
        post_data = request.get_json()
        try:
            provision_id = post_data.get('provision_id')
            provision_type = post_data.get('provision_type')
            provision_status = post_data.get('provision_status')
            is_updated = False
            mapped_provision_type = ''
            tws_result = ''

            if provision_type == 'is_ifwi':
                updated = db.session.query(ManualProvision).filter(
                    text("provision_id=:id and is_ifwi!='PASS' and is_ifwi!='FAIL' and is_ifwi!=:status")).params(
                    id=provision_id, status=provision_status).first()
                if updated:
                    updated.is_ifwi = provision_status
                    db.session.commit()
                    is_updated = True
                    mapped_provision_type = 'IFWI Provisioning'
                    tws_result = updated.tws_result_ifwi

            elif provision_type == 'is_os':
                updated = db.session.query(ManualProvision).filter(
                    text("provision_id=:id and is_os!='PASS' and is_os!='FAIL' and is_os!=:status")).params(
                    id=provision_id, status=provision_status).first()
                if updated:
                    updated.is_os = provision_status
                    db.session.commit()
                    is_updated = True
                    mapped_provision_type = 'Imaging'
                    tws_result = updated.tws_result_os

            elif provision_type == 'is_bios':
                updated = db.session.query(ManualProvision).filter(
                    text("provision_id=:id and is_bios!='PASS' and is_bios!='FAIL' and is_bios!=:status")).params(
                    id=provision_id, status=provision_status).first()
                if updated:
                    updated.is_bios = provision_status
                    db.session.commit()
                    is_updated = True
                    mapped_provision_type = 'BIOS Update'
                    tws_result = updated.tws_result_bios
            if is_updated:
                self.triggerEmail(updated, mapped_provision_type, provision_status, tws_result)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully Added Updated.',
                    'id': updated.provision_id,
                    'action': provision_type,
                    'provision_status': provision_status
                }
                return make_response(jsonify(responseObject)), 201
            else:
                responseObject = {
                    'status': 'success',
                    'message': 'No record To Updated.',
                    'id': provision_id,
                    'action': provision_type
                }
                return make_response(jsonify(responseObject)), 201

        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Add provision.'
            }
            return make_response(jsonify(responseObject)), 500

    def triggerEmail(self, updated_object: ManualProvision, provision_type, provision_status, tws_result):
        # Do changes as per sso route
        user = User.query.filter_by(user_id=updated_object.user_id).first()
        email_notifier = EmailNotifier(
            oap_req_id=updated_object.request_id,
            oap_provision_type=provision_type,
            to_list=updated_object.email,  # changed user to updated_object
            oap_user_fullname=updated_object.external_id,  # changed user to updated_object
            notification_type='trigger_status',
            oap_sut=updated_object.sut,
            oap_provision_status=provision_status,
            oap_tws_link=tws_result)
        email_notifier.trigger_email_notification()


class OapProvisionMasterAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        try:
            provision_master = ManualProvisionMaster(
                user_id=post_data.get('user_id')
            )
            db.session.add(provision_master)
            db.session.commit()
            master = db.session.query(ManualProvisionMaster).order_by(ManualProvisionMaster.global_id.desc()).first()
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Successfully Added ManualProvisionMaster.',
                'global_id': master.global_id
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Add ManualProvisionMaster.'
            }
            return make_response(jsonify(responseObject)), 500

    def get(self):
        try:
            master = db.session.query(ManualProvisionMaster).order_by(ManualProvisionMaster.global_id.desc()).first()
            json_string = json.dumps(master, cls=AlchemyEncoder)
            responseObject = {
                'status': 'success',
                'data': json.loads(json_string)
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Fetch Controller.',
                'description': e
            }
            return make_response(jsonify(responseObject)), 500


class PingAPI(MethodView):
    def get(self):
        responseObject = {
            'status': 'success',
            'message': 'Welcome to OAP Middle Tier Services!!'
        }
        return make_response(jsonify(responseObject)), 200


class ControllerAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        try:
            controller = Controller(
                controller_name=post_data.get('controller'),
                group_id=post_data.get('group'),
                alias_name=post_data.get('alias_name')
            )
            db.session.add(controller)
            db.session.commit()
            responseObject = {
                'status': 'success',
                'message': 'Successfully Added Controller.'
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Add Controller.'
            }
            return make_response(jsonify(responseObject)), 500

    def get(self):
        try:
            controllers = Controller.query.all()
            json_string = json.dumps([ob for ob in controllers], cls=AlchemyEncoder)
            responseObject = {
                'status': 'success',
                'data': json.loads(json_string)
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Fetch Controller.',
                'description': e
            }
            return make_response(jsonify(responseObject)), 500


class PlatformAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        try:
            platform = Platform(
                platform_name=post_data.get('platform'),
                alias_name=post_data.get('alias'),
                controller_id=post_data.get('controller_id')
            )
            db.session.add(platform)
            db.session.commit()
            responseObject = {
                'status': 'success',
                'message': 'Successfully Added Platform.'
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Add Platform.'
            }
            return make_response(jsonify(responseObject)), 500

    def get(self):
        try:
            platforms = Platform.query.all()
            json_string = json.dumps([ob for ob in platforms], cls=AlchemyEncoder)
            responseObject = {
                'status': 'success',
                'data': json.loads(json_string)
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Fetch Platform.',
                'description': e
            }
            return make_response(jsonify(responseObject)), 500


oap_blueprint = Blueprint('oap', __name__)

ping_view = PingAPI.as_view('ping_view')
controller_view = ControllerAPI.as_view('controller_view')
platform_view = PlatformAPI.as_view('platform_view')
provision_master_view = OapProvisionMasterAPI.as_view('provision_master_view')
provision_view = OapProvisionAPI.as_view('provision_view')
sutstatus_view = SUTStatusForControllerAPI.as_view('sutstatus_view')
# add Rules for API Endpoints

oap_blueprint.add_url_rule(
    '/oap/controller/sutstatus',
    view_func=sutstatus_view,
    methods=['GET']
)
oap_blueprint.add_url_rule(
    '/',
    view_func=ping_view,
    methods=['GET']
)
oap_blueprint.add_url_rule(
    '/oap/controller',
    view_func=controller_view,
    methods=['GET', 'POST']
)
oap_blueprint.add_url_rule(
    '/oap/platform',
    view_func=platform_view,
    methods=['GET', 'POST']
)
oap_blueprint.add_url_rule(
    '/oap/provision_master',
    view_func=provision_master_view,
    methods=['GET', 'POST']
)
oap_blueprint.add_url_rule(
    '/oap/provision',
    view_func=provision_view,
    methods=['GET', 'POST', 'PATCH']
)
