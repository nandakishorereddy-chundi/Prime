# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from cProfile import label
from pprint import isreadable
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

#user table
auth.settings.extra_fields['auth_user'] = [
    Field('phone_number', 'string', requires = IS_NOT_EMPTY()),
    Field('designation', 'string', requires = IS_NOT_EMPTY()),
    Field('IS_ADMIN', 'boolean', default = False, readable = False, writable = False)]
## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

import datetime

# Customer, Project and Product Data
db.define_table('organization',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('address', 'text', requires=IS_NOT_EMPTY()))
db.define_table('point_of_contact',
                db.Field('organization_id', db.organization, readable = False, writable = False),
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('email', 'string', requires=IS_EMAIL()),
                db.Field('phone_number', 'string', requires=IS_NOT_EMPTY()),
                db.Field('designation', 'string'))
db.define_table('project',
                db.Field('organization_id', db.organization, readable = False, writable = False),
                db.Field('name', 'string', readable = False, writable = False, requires=IS_NOT_EMPTY()),
                db.Field('address', 'text'),
                db.Field('description', 'text'),
                db.Field('registered_date', 'date', writable = False),
                db.Field('phase', 'string', requires=IS_IN_SET(['Enquiry','Order Confirmed','Measurements','Production','Dispatched','Installed','Completed','Cancelled']), default='Enquiry'))
db.define_table('project_to_poc',
                db.Field('project_id', db.project),
                db.Field('poc_id', db.point_of_contact))
db.define_table('documents',
                db.Field('project_id', db.project, readable = False, writable = False),
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('document_type', 'string', requires=IS_IN_SET(['Quotation', 'Production Document', 'Raw Material Report', 'Completion Letter', 'Other']), label='Type'),
                db.Field('document_file', 'upload', requires=IS_UPLOAD_FILENAME(extension='pdf|doc|docx|odt|txt|jpg|png|jpeg'), label='File', autodelete = True),
                db.Field('upload_time', 'datetime', readable = False, writable = False))
db.define_table('design',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('description', 'text'),
                db.Field('design_image', 'upload', requires = IS_IMAGE(extensions=('jpeg', 'jpg')), comment = 'Images can be jpg and jpeg files only'))
db.define_table('installation_details',
                db.Field('name','string', requires=IS_NOT_EMPTY()),
                db.Field('phone_number','string', requires=IS_NOT_EMPTY()))
db.define_table('product',
                db.Field('name', 'string'),
                db.Field('design_id', db.design),
                db.Field('project_id', db.project, writable = False),
                db.Field('phase', 'string', requires=IS_IN_SET(['Started', 'Production', 'Delivery', 'Installation', 'Completed', 'Cancelled']), default = 'Started', writable = False),
                db.Field('installed_by', db.installation_details, readable=False, writable=False),
                db.Field('block_number', 'string'),
                db.Field('flat_number', 'string'),
                db.Field('window_number', 'string'),
                db.Field('extra_comment', 'text'))

# Inventory Management
db.define_table('profile',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('profile_code', 'string'),
                db.Field('category', 'string', requires=IS_IN_SET(['Main', 'Bead', 'Interlock', 'Auxilliary'])),
                db.Field('description', 'text'),
                db.Field('weight', 'double', requires=IS_NOT_EMPTY()),
                db.Field('profile_length', 'double', label = 'Length', requires=IS_NOT_EMPTY()),
                db.Field('number_of_pieces', 'integer', requires=IS_NOT_EMPTY()),
                db.Field('price', 'double', requires=IS_NOT_EMPTY()),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()))
db.define_table('reinforcement',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('description', 'text'),
                db.Field('weight', 'double', requires=IS_NOT_EMPTY()),
                db.Field('reinforcement_length', 'double', label = 'Length', requires=IS_NOT_EMPTY()),
                db.Field('number_of_pieces', 'integer', requires=IS_NOT_EMPTY()),
                db.Field('price', 'double', requires=IS_NOT_EMPTY()),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()))
db.define_table('hardware_and_accessories',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('description', 'text'),
                db.Field('price', 'double', requires=IS_NOT_EMPTY()),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()))
db.define_table('glass',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('description', 'text'),
                db.Field('price', 'double', requires=IS_NOT_EMPTY()),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()))
db.define_table('installation_material',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('description', 'text'),
                db.Field('price', 'double', requires=IS_NOT_EMPTY()),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()))
db.define_table('profit_margin_table',
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('percentage', 'double', requires=IS_NOT_EMPTY()))

# Design
db.define_table('design_parameters',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('codename', 'string', writable = False))
db.define_table('profile_used_in_design',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('profile_id', db.profile),
                db.Field('profile_position', 'string', requires=IS_IN_SET(['W', 'H']), label = 'Position'),
                db.Field('cut', 'string', requires=IS_IN_SET(['/', '\\'])),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()),
                db.Field('length_calculation', 'string', requires=IS_NOT_EMPTY()),
                db.Field('cost_calculation', 'string', requires=IS_NOT_EMPTY()))
db.define_table('reinforcement_used_in_design',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('reinforcement_id', db.reinforcement),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()),
                db.Field('length_calculation', 'string', requires=IS_NOT_EMPTY()),
                db.Field('cost_calculation', 'string', requires=IS_NOT_EMPTY()))
db.define_table('hardware_and_accessories_used_in_design',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('hardware_and_accessories_id', db.hardware_and_accessories),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()),
                db.Field('cost_calculation', 'string', requires=IS_NOT_EMPTY()))
db.define_table('glass_used_in_design',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('glass_id', db.glass),
                db.Field('width_calculation', 'string', requires=IS_NOT_EMPTY()),
                db.Field('height_calculation', 'string', requires=IS_NOT_EMPTY()),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()),
                db.Field('cost_calculation', 'string', requires=IS_NOT_EMPTY()))
db.define_table('installation_material_used_in_design',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('installation_material_id', db.installation_material),
                db.Field('quantity', 'double', requires=IS_NOT_EMPTY()),
                db.Field('cost_calculation', 'string', requires=IS_NOT_EMPTY()))
db.define_table('extra_information_in_design',
                db.Field('design_id', db.design, readable = False, writable = False),
                db.Field('name', 'string', requires=IS_NOT_EMPTY()),
                db.Field('default_value', 'string', label = 'Value'),
                db.Field('calculation', 'string'))

# Product Values
db.define_table('design_parameters_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('design_parameter_id', db.design_parameters),
                db.Field('parameter_value', 'double', label = 'Value'))
db.define_table('profile_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('profile_used_in_design_id', db.profile_used_in_design, writable = False),
                db.Field('profile_position', 'string', requires=IS_IN_SET(['W', 'H']), label = 'Position'),
                db.Field('cut', 'string', requires=IS_IN_SET(['/', '\\'])),
                db.Field('length_value', 'double', label = 'Length'),
                db.Field('quantity', 'double'),
                db.Field('profile_cost', 'double', label = 'Cost'))
db.define_table('reinforcement_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('reinforcement_used_in_design_id', db.reinforcement_used_in_design, writable = False),
                db.Field('length_value', 'double', label = 'Length'),
                db.Field('quantity', 'double'),
                db.Field('reinforcement_cost', 'double', label = 'Cost'))
db.define_table('hardware_and_accessories_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('hardware_and_accessories_used_in_design_id', db.hardware_and_accessories_used_in_design, writable = False),
                db.Field('quantity', 'double'),
                db.Field('hardware_and_accessories_cost', 'double', label = 'Cost'))
db.define_table('glass_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('glass_used_in_design_id', db.glass_used_in_design, writable = False),
                db.Field('width', 'double'),
                db.Field('height', 'double'),
                db.Field('quantity', 'double'),
                db.Field('glass_cost', 'double', label = 'Cost'))
db.define_table('installation_material_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('installation_material_used_in_design_id', db.installation_material_used_in_design, writable = False),
                db.Field('quantity', 'double'),
                db.Field('installation_material_cost', 'double', label = 'Cost'))
db.define_table('extra_information_values',
                db.Field('product_id', db.product, writable = False),
                db.Field('extra_information_in_design_id', db.extra_information_in_design, writable = False),
                db.Field('default_value', 'string', label = 'Value'),
                db.Field('extra_information_value', 'double', label = 'Value'))
db.define_table('product_cost',
                db.Field('product_id', db.product, writable = False),
                db.Field('profile_cost', 'double'),
                db.Field('reinforcement_cost', 'double'),
                db.Field('hardware_and_accessories_cost', 'double'),
                db.Field('glass_cost', 'double'),
                db.Field('installation_material_cost', 'double'),
                db.Field('fabrication_cost', 'double'),
                db.Field('installation_cost', 'double'),
                db.Field('total_value', 'double'),
                db.Field('profit_margin_id', db.profit_margin_table),
                db.Field('final_value', 'double'))

#Quotation
db.define_table('product_in_quotation',
                db.Field('document_id', db.documents, readable = False, writable = False),
                db.Field('design_id', db.design),
                db.Field('name', 'string'),
                db.Field('quantity', 'integer'),
                db.Field('profile_cost', 'double'),
                db.Field('reinforcement_cost', 'double'),
                db.Field('hardware_and_accessories_cost', 'double'),
                db.Field('glass_cost', 'double'),
                db.Field('installation_material_cost', 'double'),
                db.Field('fabrication_cost', 'double'),
                db.Field('installation_cost', 'double'),
                db.Field('total_value', 'double'),
                db.Field('profit_margin_id', db.profit_margin_table),
                db.Field('final_value', 'double'),
                db.Field('total_value_per_piece', 'double'))
db.define_table('product_quotation_parameter_values',
                db.Field('product_in_quotation_id', db.product_in_quotation, writable = False),
                db.Field('design_parameter_id', db.design_parameters),
                db.Field('parameter_value', 'double', label = 'Value'))
db.define_table('product_quotation_glass_values',
                db.Field('product_in_quotation_id', db.product_in_quotation, writable = False),
                db.Field('glass_used_in_design_id', db.glass_used_in_design, writable = False),
                db.Field('width', 'double'),
                db.Field('height', 'double'),
                db.Field('quantity', 'double'),
                db.Field('glass_cost', 'double', label = 'Cost'))
db.define_table('product_quotation_hardware_values',
                db.Field('product_in_quotation_id', db.product_in_quotation, writable = False),
                db.Field('hardware_and_accessories_used_in_design_id', db.hardware_and_accessories_used_in_design, writable = False),
                db.Field('quantity', 'double'),
                db.Field('hardware_and_accessories_cost', 'double', label = 'Cost'))
db.define_table('product_quotation_extra_information_values',
                db.Field('product_in_quotation_id', db.product_in_quotation, writable = False),
                db.Field('extra_information_in_design_id', db.extra_information_in_design),
                db.Field('default_value', 'string', label = 'Value'),
                db.Field('extra_information_value', 'double', label = 'Value'))
db.define_table('choose_design_parameters',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('param_id', db.design_parameters))
db.define_table('choose_profile',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('pro_id', db.profile))
db.define_table('choose_reinforcement',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('rein_id', db.reinforcement))
db.define_table('choose_hardware',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('hardware_id', db.hardware_and_accessories))
db.define_table('choose_glass',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('glas_id', db.glass))
db.define_table('choose_material',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('material_id', db.installation_material))
db.define_table('choose_extra',
                db.Field('product_in_quotation_id', db.product_in_quotation),
                db.Field('extra_info_id', db.extra_information_in_design))

#Logging
db.define_table('logs',
                db.Field('log_message','text'),
                db.Field('log_time', 'datetime'))

db.point_of_contact.organization_id.requires = IS_IN_DB(db,db.organization.id,'%(name)s')
db.point_of_contact.phone_number.requires = IS_NOT_IN_DB(db,'point_of_contact.phone_number')
db.project.organization_id.requires = IS_IN_DB(db,db.organization.id,'%(name)s')
db.project_to_poc.project_id.requires = IS_IN_DB(db,db.project.id,'%(name)s %(address)s %(description)s')
db.project_to_poc.poc_id.requires = IS_IN_DB(db,db.point_of_contact.id,'%(name)s %(phone_number)s')
db.documents.project_id.requires = IS_IN_DB(db,db.project.id,'%(name)s %(address)s %(description)s')
db.design.name.requires = IS_NOT_IN_DB(db, 'design.name')
db.product.design_id.requires = IS_IN_DB(db,db.design.id,'%(name)s')
db.product.project_id.requires = IS_IN_DB(db,db.project.id,'%(name)s %(address)s %(description)s')
db.product.installed_by.requires = IS_IN_DB(db,db.installation_details.id,'%(name)s %(phone_number)s')

db.profile.profile_code.requires = IS_NOT_IN_DB(db, 'profile.profile_code')
db.profit_margin_table.name.requires = IS_NOT_IN_DB(db, 'profit_margin_table.name')

db.design_parameters.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.design_parameters.name.requires = IS_NOT_IN_DB(db, db.design_parameters.name)
db.profile_used_in_design.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.profile_used_in_design.profile_id.requires = IS_IN_DB(db, db.profile.id, '%(name)s %(profile_code)s')
db.reinforcement_used_in_design.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.reinforcement_used_in_design.reinforcement_id.requires = IS_IN_DB(db, db.reinforcement.id, '%(name)s')
db.hardware_and_accessories_used_in_design.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.hardware_and_accessories_used_in_design.hardware_and_accessories_id.requires = IS_IN_DB(db, db.hardware_and_accessories.id, '%(name)s')
db.glass_used_in_design.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.glass_used_in_design.glass_id.requires = IS_IN_DB(db, db.glass.id, '%(name)s')
db.installation_material_used_in_design.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.installation_material_used_in_design.installation_material_id.requires = IS_IN_DB(db, db.installation_material.id, '%(name)s')
db.extra_information_in_design.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.extra_information_in_design.name.requires = IS_NOT_IN_DB(db, db.extra_information_in_design.name)

db.design_parameters_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.design_parameters_values.design_parameter_id.requires = IS_IN_DB(db, db.design_parameters.id, '%(name)s')
db.profile_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.profile_values.profile_used_in_design_id.requires = IS_IN_DB(db, db.profile_used_in_design.id, '%(profile_id)s')
db.reinforcement_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.reinforcement_values.reinforcement_used_in_design_id.requires = IS_IN_DB(db, db.reinforcement_used_in_design.id, '%(reinforcement_id)s')
db.hardware_and_accessories_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.hardware_and_accessories_values.hardware_and_accessories_used_in_design_id.requires = IS_IN_DB(db, db.hardware_and_accessories_used_in_design.id, '%(hardware_and_accessories_id)s')
db.glass_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.glass_values.glass_used_in_design_id.requires = IS_IN_DB(db, db.glass_used_in_design.id, '%(glass_id)s')
db.installation_material_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.installation_material_values.installation_material_used_in_design_id.requires = IS_IN_DB(db, db.installation_material_used_in_design.id, '%(installation_material_id)s')
db.extra_information_values.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.extra_information_values.extra_information_in_design_id.requires = IS_IN_DB(db, db.extra_information_in_design.id, '%(name)s')
db.product_cost.product_id.requires = IS_IN_DB(db, db.product.id, '%(name)s')
db.product_cost.profit_margin_id.requires = IS_IN_DB(db, db.profit_margin_table.id, '%(name)s')

db.product_in_quotation.document_id.requires = IS_IN_DB(db, db.documents.id, '%(name)s')
db.product_in_quotation.design_id.requires = IS_IN_DB(db, db.design.id, '%(name)s')
db.product_in_quotation.profit_margin_id.requires = IS_IN_DB(db, db.profit_margin_table.id, '%(name)s')
db.product_quotation_parameter_values.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation, '%(document_id)s')
db.product_quotation_parameter_values.design_parameter_id.requires = IS_IN_DB(db, db.design_parameters, '%(name)s')
db.product_quotation_glass_values.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation, '%(document_id)s')
db.product_quotation_glass_values.glass_used_in_design_id.requires = IS_IN_DB(db, db.glass_used_in_design, '%(glass_id)s')
db.product_quotation_hardware_values.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation, '%(document_id)s')
db.product_quotation_hardware_values.hardware_and_accessories_used_in_design_id.requires = IS_IN_DB(db, db.hardware_and_accessories_used_in_design, '%(hardware_and_accessories_id)s')
db.product_quotation_extra_information_values.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation, '%(document_id)s')
db.product_quotation_extra_information_values.extra_information_in_design_id.requires = IS_IN_DB(db, db.extra_information_in_design, '%(name)s')
db.choose_design_parameters.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_profile.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_reinforcement.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_hardware.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_glass.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_material.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_extra.product_in_quotation_id.requires = IS_IN_DB(db, db.product_in_quotation.id, '%(name)s')
db.choose_design_parameters.param_id.requires = IS_IN_DB(db, db.design_parameters.id, '%(name)s')
db.choose_profile.pro_id.requires = IS_IN_DB(db, db.profile.id, '%(name)s')
db.choose_reinforcement.rein_id.requires = IS_IN_DB(db, db.reinforcement.id, '%(name)s')
db.choose_hardware.hardware_id.requires = IS_IN_DB(db, db.hardware_and_accessories.id, '%(name)s')
db.choose_glass.glas_id.requires = IS_IN_DB(db, db.glass.id, '%(name)s')
db.choose_material.material_id.requires = IS_IN_DB(db, db.installation_material.id, '%(name)s')
db.choose_extra.extra_info_id.requires = IS_IN_DB(db, db.extra_information_in_design.id, '%(name)s')