# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from ctypes import cast
import re
import sys
import collections
import os
from types import *

#region Default
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome")
    org_table = db(db.organization.id >= 0).select()
    POC_table = db(db.point_of_contact.id >= 0).select()
    Installation_details_table = db(db.installation_details.id >=0 ).select()
    return dict(message=T('Welcome to web2py!'), org_table = org_table, POC_table = POC_table, Installation_details_table = Installation_details_table)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
#endregion

from gluon.tools import Crud
crud = Crud(db)
crud.settings.controller = 'default'

from gluon.contrib.pyfpdf import FPDF,HTMLMixin
from plugin_sqleditable.editable import SQLEDITABLE
SQLEDITABLE.init()

#region Admin Functions
#############################################################################################################
#------------------------------------------- ADMIN FUNCTIONS -----------------------------------------------#
#############################################################################################################
@auth.requires_login()
def admin_functions():
    profit_table = db(db.profit_margin_table.id >= 0).select()
    grid = SQLFORM.grid(db.profit_margin_table)
    design_table = db(db.design.id >= 0).select()
    return dict(profit_table = profit_table,design_table = design_table, grid = grid)

#region Admin/User
#-------------------------------------------- ADD/DELETE ADMIN/USER -----------------------------------------#
@auth.requires_login()
def add_new_admin():
    user_table = db((db.auth_user.id >= 0) & (db.auth_user.id != auth.user.id) & (db.auth_user.IS_ADMIN == False)).select()
    return dict(user_table = user_table)
@auth.requires_login()
def add_new_admin_helper():
    if auth.user.IS_ADMIN:
        new_admin = []
        for var in request.vars:
            try:
                new_admin.append(int(var))
            except:
                pass
        new_admin_list = db((db.auth_user. id >= 0) & (db.auth_user.id.belongs(new_admin))).select()
        for user in new_admin_list:
            user.IS_ADMIN = True
            user.update_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' made ' + user.first_name + ' ' + user.last_name + ' admin', log_time = datetime.datetime.now())
        redirect('admin_functions.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def remove_admin():
    user_table = db((db.auth_user.id >= 0) & (db.auth_user.id != auth.user.id) & (db.auth_user.IS_ADMIN == True)).select()
    return dict(user_table = user_table)
@auth.requires_login()
def remove_admin_helper():
    if auth.user.IS_ADMIN:
        admin = []
        for var in request.vars:
            try:
                admin.append(int(var))
            except:
                pass
        admin_list = db((db.auth_user. id >= 0) & (db.auth_user.id.belongs(admin))).select()
        for user in admin_list:
            user.IS_ADMIN = False
            user.update_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed admin status of ' + user.first_name + ' ' + user.last_name, log_time = datetime.datetime.now())
        redirect('admin_functions.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def remove_user():
    if auth.user.IS_ADMIN:
        user_table = db((db.auth_user.id >= 0) & (db.auth_user.id != auth.user.id)).select()
        return dict(user_table = user_table)
    else:
        response.flash = 'Requires Admin Access'
@auth.requires_login()
def remove_user_helper():
    if auth.user.IS_ADMIN:
        user_list = []
        for var in request.vars:
            try:
                user_list.append(int(var))
            except:
                pass
        new_user_list = db((db.auth_user. id >= 0) & (db.auth_user.id.belongs(user_list))).select()
        for user in new_user_list:
            user.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed user ' + user.first_name + ' ' + user.last_name, log_time = datetime.datetime.now())
        redirect('admin_functions.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'
#endregion

#region Profit Margin Table
#-------------------------------------------- ADD/DELETE/UPDATE/VIEW PROFIT MARGIN TABLE -----------------------------------------#
@auth.requires_login()
def add_profit_margin_entry():
    if auth.user.IS_ADMIN:
        form = SQLFORM(db.profit_margin_table)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted profit margin table entry ' + form.vars.name + ' ---- ' + form.vars.percentage, log_time = datetime.datetime.now())
            redirect(URL('admin_functions.html'))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_profit_margin_entry():
    if auth.user.IS_ADMIN:
        entry_id = request.vars.entry_id
        l=db(db.profit_margin_table.id==entry_id).select()
        form=[]
        for i in l:
            old_name = i.name
            old_percentage = i.percentage
            form = SQLFORM(db.profit_margin_table, i, deletable=False)
            if form.process().accepted:
                response.flash = 'form accepted'
                if not request.vars.delete_this_record:
                    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated profit margin table entry ' + old_name + ' ---- ' + str(old_percentage) + ' to ' + form.vars.name + ' ---- ' + str(form.vars.percentage), log_time = datetime.datetime.now())
                else:
                    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted profit margin table entry ' + old_name, log_time = datetime.datetime.now())
                redirect(URL('admin_functions.html'))
            elif form.errors:
               response.flash = 'form has errors'
            else:
               response.flash = 'please update'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'
#endregion

#region Design
#------------------------------------------- ADD DESIGN -----------------------------------------#
@auth.requires_login()
def add_design():
    if auth.user.IS_ADMIN:
        form = SQLFORM(db.design)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' added design ' + form.vars.name, log_time = datetime.datetime.now())
            redirect(URL('add_design_parameters.html', args = form.vars.id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_design_parameters():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast = int)
        return dict(design_id = design_id)
    else:
        response.flash = 'Requires Admin Access'
@auth.requires_login()
def add_design_parameters_helper():
    #Update logs
    if auth.user.IS_ADMIN:
        design_name = db(db.design.id == request.vars.design_id).select()
        params = request.vars.params.split(',')
        for i in range(len(params)):
            db.design_parameters.insert(design_id=request.vars.design_id,name=params[i],codename='P' + str(i+1))
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' added ' + str(len(params)) + ' design parameters to design ' + design_name[0].name, log_time = datetime.datetime.now())
        redirect(URL('add_profile_used_in_design.html',args=request.vars.design_id))
        return dict()
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_profile_used_in_design():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        design_name = db(db.design.id == design_id).select()
        profile_name = db(db.profile.id == form.vars.profile_id).select()
        grid = SQLFORM.grid(db.design_parameters.design_id == design_id,args=request.args[:1],fields=[db.design_parameters.name,db.design_parameters.codename],searchable=False,sortable=False,deletable=False,editable=False,create=False,details=False,csv=False)
        profile_table = db(db.profile_used_in_design.design_id == design_id).select()
        form = SQLFORM(db.profile_used_in_design,buttons=[TAG.button("Add these details",_type="submit"),TAG.button("Done",_type="button",_onClick="confirm_button()")])
        names = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
        db.profile_used_in_design.design_id.default = design_id
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted profile details name: ' + profile_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('add_profile_used_in_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please fill the form'
        return dict(grid = grid,design_id = design_id,form = form,profile_table = profile_table,names = names)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_reinforcement_used_in_design():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        design_name = db(db.design.id == design_id).select()
        reinforcement_name = db(db.reinforcement.id == form.vars.reinforcement_id).select()
        grid = SQLFORM.grid(db.design_parameters.design_id == design_id,args=request.args[:1],fields=[db.design_parameters.name,db.design_parameters.codename],searchable=False,sortable=False,deletable=False,editable=False,create=False,details=False,csv=False)
        reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select()
        names = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
        db.reinforcement_used_in_design.design_id.default = design_id
        form = SQLFORM(db.reinforcement_used_in_design,buttons=[TAG.button("Add these details",_type="submit"),TAG.button("Done",_type="button",_onClick="confirm_button()")])
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted reinforcement details name: ' + reinforcement_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('add_reinforcement_used_in_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please fill the form'
        return dict(grid = grid,design_id = design_id,form = form,reinforcement_table = reinforcement_table,names = names)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_HAA_used_in_design():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        design_name = db(db.design.id == design_id).select()
        HAA_name = db(db.hardware_and_accessories.id == form.vars.hardware_and_accessories_id).select()
        grid = SQLFORM.grid(db.design_parameters.design_id == design_id,args=request.args[:1],fields=[db.design_parameters.name,db.design_parameters.codename],searchable=False,sortable=False,deletable=False,editable=False,create=False,details=False,csv=False)
        HAA_table = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select()
        names = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))
        db.hardware_and_accessories_used_in_design.design_id.default = design_id
        form = SQLFORM(db.hardware_and_accessories_used_in_design,buttons=[TAG.button("Add these details",_type="submit"),TAG.button("Done",_type="button",_onClick="confirm_button()")])
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted hardware details name: ' + HAA_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('add_HAA_used_in_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please fill the form'
        return dict(grid = grid,design_id = design_id,form = form,HAA_table = HAA_table,names = names)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_glass_used_in_design():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        design_name = db(db.design.id == design_id).select()
        glass_name = db(db.glass.id == form.vars.glass_id).select()
        grid = SQLFORM.grid(db.design_parameters.design_id == design_id,args=request.args[:1],fields=[db.design_parameters.name,db.design_parameters.codename],searchable=False,sortable=False,deletable=False,editable=False,create=False,details=False,csv=False)
        glass_table = db(db.glass_used_in_design.design_id == design_id).select()
        names = db(db.glass_used_in_design.design_id == design_id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
        db.glass_used_in_design.design_id.default = design_id
        form = SQLFORM(db.glass_used_in_design,buttons=[TAG.button("Add these details",_type="submit"),TAG.button("Done",_type="button",_onClick="confirm_button()")])
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted glass details name: ' + glass_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('add_glass_used_in_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please fill the form'
        return dict(grid = grid,design_id = design_id,form = form,glass_table = glass_table,names = names)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_material_used_in_design():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        design_name = db(db.design.id == design_id).select()
        material_name = db(db.installation_material.id == form.vars.installation_material_id).select()
        grid = SQLFORM.grid(db.design_parameters.design_id == design_id,args=request.args[:1],fields=[db.design_parameters.name,db.design_parameters.codename],searchable=False,sortable=False,deletable=False,editable=False,create=False,details=False,csv=False)
        material_table = db(db.installation_material_used_in_design.design_id == design_id).select()
        names = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
        db.installation_material_used_in_design.design_id.default = design_id
        form = SQLFORM(db.installation_material_used_in_design,buttons=[TAG.button("Add these details",_type="submit"),TAG.button("Done",_type="button",_onClick="confirm_button()")])
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted installation material details name: ' + material_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('add_material_used_in_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please fill the form'
        return dict(grid = grid,design_id = design_id,form = form,material_table = material_table,names = names)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_extra_information_in_design():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        design_name = db(db.design.id == design_id).select()
        grid = SQLFORM.grid(db.design_parameters.design_id == design_id,args=request.args[:1],fields=[db.design_parameters.name,db.design_parameters.codename],searchable=False,sortable=False,deletable=False,editable=False,create=False,details=False,csv=False)
        extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()
        db.extra_information_in_design.design_id.default = design_id
        form = SQLFORM(db.extra_information_in_design,buttons=[TAG.button("Add these details",_type="submit"),TAG.button("Done",_type="button",_onClick="confirm_button()")])
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted extra_information name: ' + form.vars.name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('add_extra_information_in_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please fill the form'
        return dict(grid = grid,design_id = design_id,form = form,extra_information_table = extra_information_table)#,names = names)
    else:
        response.flash = 'Requires Admin Access'

#------------------------------------------- REMOVE DESIGN -----------------------------------------#
@auth.requires_login()
def remove_design():
    if auth.user.IS_ADMIN:
        design_table = db(db.design.id > 0).select()
        return dict(design_table = design_table)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def remove_design_helper():
    if auth.user.IS_ADMIN:
        design_list = []
        for var in request.vars:
            try:
                design_list.append(int(var))
            except:
                pass
        new_design_list = db((db.design.id >= 0) & (db.design.id.belongs(design_list))).select()
        for design in new_design_list:

            #Deleting associated values
            design_parameters_list = db(db.design_parameters.design_id == design.id).select()
            for parameter in design_parameters_list:
                parameter.delete_record()

            profile_list = db(db.profile_used_in_design.design_id == design.id).select()
            for profile in profile_list:
                profile.delete_record()

            reinforcement_list = db(db.reinforcement_used_in_design.design_id == design.id).select()
            for reinforcement in reinforcement_list:
                reinforcement.delete_record()

            hardware_list = db(db.hardware_and_accessories_used_in_design.design_id == design.id).select()
            for hardware in hardware_list:
                profile.delete_record()

            glass_list = db(db.glass_used_in_design.design_id == design.id).select()
            for glass in glass_list:
                glass.delete_record()

            material_list = db(db.installation_material_used_in_design.design_id == design.id).select()
            for material in material_list:
                material.delete_record()

            extra_information_list = db(db.extra_information_in_design.design_id == design.id).select()
            for info in extra_information_list:
                info.delete_record()

            #Deleting Quotation related entries for design
            quotation_product_list = db(db.product_in_quotation.design_id == design.id).select()
            for product in quotation_product_list:

                product_quotation_parameter_values_list = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select()
                for parameter in product_quotation_parameter_values_list:
                    parameter.delete_record()

                product_quotation_glass_values_list = db(db.product_quotation_glass_values.product_in_quotation_id == product.id).select()
                for glass in product_quotation_glass_values_list:
                    glass.delete_record()

                product_quotation_hardware_values_list = db(db.product_quotation_hardware_values.product_in_quotation_id == product.id).select()
                for hardware in product_quotation_hardware_values_list:
                    hardware.delete_record()

                product_quotation_extra_information_values_list = db(db.product_quotation_extra_information_values.product_in_quotation_id == product.id).select()
                for info in product_quotation_extra_information_values_list:
                    info.delete_record()
                product.delete_record()

                parameter_table = db(db.choose_design_parameters.product_in_quotation_id == product.id).select()
                for i in parameter_table:
                    i.delete_record()
                profile_table = db(db.choose_profile.product_in_quotation_id == product.id).select()
                for i in profile_table:
                    i.delete_record()
                reinforcement_table = db(db.choose_reinforcement.product_in_quotation_id == product.id).select()
                for i in reinforcement_table:
                    i.delete_record()
                HAA_table = db(db.choose_hardware.product_in_quotation_id == product.id).select()
                for i in HAA_table:
                    i.delete_record()
                glass_table = db(db.choose_glass.product_in_quotation_id == product.id).select()
                for i in glass_table:
                    i.delete_record()
                material_table = db(db.choose_material.product_in_quotation_id == product.id).select()
                for i in material_table:
                    i.delete_record()
                extra_info_table = db(db.choose_extra.product_in_quotation_id == product.id).select()
                for i in extra_info_table:
                    i.delete_record()

            #Deleting Products and associated entries
            product_list = db(db.product.design_id == design.id).select()
            for entry in product_list:

                design_parameters_values_list = db(db.design_parameters_values.product_id == entry.id).select()
                for parameter in design_parameters_values_list:
                    parameter.delete_record()

                profile_values_list = db(db.profile_values.product_id == entry.id).select()
                for profile in profile_values_list:
                    profile.delete_record()

                reinforcement_values_list = db(db.reinforcement_values.product_id == entry.id).select()
                for reinforcement in reinforcement_values_list:
                    reinforcement.delete_record()

                hardware_and_accessories_values_list = db(db.hardware_and_accessories_values.product_id == entry.id).select()
                for hardware in hardware_and_accessories_values_list:
                    hardware.delete_record()

                glass_values_list = db(db.glass_values.product_id == entry.id).select()
                for glass in glass_values_list:
                    glass.delete_record()

                installation_material_values_list = db(db.installation_material_values.product_id == entry.id).select()
                for material in installation_material_values_list:
                    material.delete_record()

                extra_information_values_list = db(db.extra_information_values.product_id == entry.id).select()
                for info in extra_information_values_list:
                    info.delete_record()

                product_cost_list = db(db.product_cost.product_id == entry.id).select()
                for cost in product_cost_list:
                    cost.delete_record()
                entry.delete_record()
            design.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed design ' + design.name, log_time = datetime.datetime.now())
        redirect('admin_functions.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'

#------------------------------------------- VIEW/UPDATE DESIGN -----------------------------------------#
@auth.requires_login()
def view_design():
    if auth.user.IS_ADMIN:
        design_id = None
        if request.vars.entry_id:
            design_id = request.vars.entry_id
        else:
            design_id = request.args(0, cast=int)
        design_table = db(db.design.id == design_id).select()
        design_parameters_table = db(db.design_parameters.design_id == design_id).select()
        profile_table = db(db.profile_used_in_design.design_id == design_id).select()
        profile_names = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
        reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select()
        reinforcement_names = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
        HAA_table = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select()
        HAA_names = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))
        glass_table = db(db.glass_used_in_design.design_id == design_id).select()
        glass_names = db(db.glass_used_in_design.design_id == design_id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
        material_table = db(db.installation_material_used_in_design.design_id == design_id).select()
        material_names = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
        extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()
        return dict(design_id = design_id, design_table = design_table, design_parameters_table = design_parameters_table, profile_table = profile_table, profile_names = profile_names, reinforcement_table = reinforcement_table, reinforcement_names = reinforcement_names, HAA_table = HAA_table, HAA_names = HAA_names, glass_table = glass_table, glass_names = glass_names, material_table = material_table, material_names = material_names, extra_information_table = extra_information_table)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_design():
    if auth.user.IS_ADMIN:
        design_id = request.vars.design_id
        design = db(db.design.id == design_id).select()
        form = []
        for i in design:
            form = SQLFORM(db.design, i, showid=False)
        if form.process().accepted:
            response.flash='Form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated design details' + i.name, log_time = datetime.datetime.now())
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(design_id = design_id,form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_design_parameters():
    if auth.user.IS_ADMIN:
        parameter_id = request.args(0,cast=int)
        design_parameter = db(db.design_parameters.id == parameter_id).select()
        form = []
        design_id = None
        old_name = ''
        design_name = []
        for i in design_parameter:
            form = SQLFORM(db.design_parameters, i, showid=False)
            design_id = i.design_id
            old_name = i.name
            design_name = db(db.design.id == i.design_id).select()
        if form.process().accepted:
            """if request.vars.delete_this_record:
                codename = ''
                for i in design_parameter:
                    codename = i.codename
                    codename = int(codename.split('P')[1])
                    parameters = db(db.design_parameters.design_id == i.design_id).select()
                    for parameter in parameters:
                        if int(parameter.codename.split('P')[1]) > codename:
                            parameter.codename = 'P' + str(int(parameter.codename.split('P')[1]) - 1)
                            parameter.update_record()
                    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted design parameter ' + i.name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:"""
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated design parameter ' + old_name + ' to ' + form.vars.name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_design_parameters():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.design_parameters.design_id.default = design_id
        design_parameter = db(db.design_parameters.design_id == design_id).select()
        max = 0
        for parameter in design_parameter:
            if max < int(parameter.codename.split('P')[1]):
                max = int(parameter.codename.split('P')[1])
        db.design_parameters.codename.default = 'P' + str(max+1)
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.design_parameters)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted design parameter ' + form.vars.name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_profile_detail():
    if auth.user.IS_ADMIN:
        profile_detail_id = request.args(0,cast=int)
        profile_detail = db(db.profile_used_in_design.id == profile_detail_id).select()
        form = []
        design_id = None
        design_name = []
        profile_name_old = []
        for i in profile_detail:
            form = SQLFORM(db.profile_used_in_design, i, showid=False, deletable=True)
            design_id = i.design_id
            profile_name_old = db(db.profile.id == i.profile_id).select()
            design_name = db(db.design.id == i.design_id).select()
        if form.process().accepted:
            values = db(db.profile_values.profile_used_in_design_id == profile_detail_id).select()
            profile_name = db(db.profile.id == form.vars.profile_id).select()
            if request.vars.delete_this_record:
                for value in values:
                    value.delete_record()

                #Reducing Cost
                product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
                for product in product_quotation_table:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    product.profile_cost -= float(Infix(convert(form.vars.cost_calculation,parameter_value)))
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted profile details name: ' + profile_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:
                for value in values:
                    try:
                        parameter_values_table = db(db.design_parameters_values.product_id == value.product_id).select(orderby=db.design_parameters_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.profile_position = form.vars.profile_position
                        value.cut = form.vars.cut
                        value.quantity = form.vars.quantity
                        value.length_value = Infix(convert(form.vars.length_calculation,parameter_value))
                        value.profile_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                try:
                    #Updating Cost
                    product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
                    for product in product_quotation_table:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))
                        product.profile_cost -= float(Infix(convert(profile_detail[0].cost_calculation,parameter_value)))
                        product.profile_cost += float(Infix(convert(form.vars.cost_calculation,parameter_value)))
                        profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                        product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                        product.total_value = product.total_value*product.quantity
                        product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                        product.total_value_per_piece = product.final_value/product.quantity
                        product.update_record()
                except:
                    pass
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated profile details name: ' + profile_name_old[0].name
                               + ' position: ' + profile_detail[0].profile_position + ' cut: ' + profile_detail[0].cut + ' quantity: ' + str(profile_detail[0].quantity)
                                + ' length_calculation: ' + profile_detail[0].length_calculation + ' cost_calculation: ' + profile_detail[0].cost_calculation + ' to ' + 'name: ' + profile_name[0].name
                                + ' position: ' + form.vars.profile_position + ' cut: ' + form.vars.cut + ' quantity: ' + str(form.vars.quantity)
                                + ' length_calculation: ' + form.vars.length_calculation + ' cost_calculation: ' + form.vars.cost_calculation + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_profile_detail():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.profile_used_in_design.design_id.default = design_id
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.profile_used_in_design)
        if form.process().accepted:
            profile_name = db(db.profile.id == form.vars.profile_id).select()
            product_table = db(db.product.design_id == design_id).select()
            product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
            for product in product_table:
                try:
                    parameter_values_table = db(db.design_parameters_values.product_id == product.id).select(orderby=db.design_parameters_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    profile_position = form.vars.profile_position
                    cut = form.vars.cut
                    quantity = form.vars.quantity
                    length_value = Infix(convert(form.vars.length_calculation,parameter_value))
                    profile_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.profile_values.insert(product_id = product.id, profile_used_in_design_id = form.vars.id, profile_position = profile_position, cut = cut, length_value = length_value, quantity = quantity, profile_cost = profile_cost)
                except:
                    pass
            for product in product_quotation_table:
                try:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    #Increasing Cost
                    profile_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    product.profile_cost += float(profile_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                except:
                    pass
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted profile details name: ' + profile_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_reinforcement_detail():
    if auth.user.IS_ADMIN:
        reinforcement_detail_id = request.args(0,cast=int)
        reinforcement_detail = db(db.reinforcement_used_in_design.id == reinforcement_detail_id).select()
        form = []
        design_id = None
        design_name = []
        reinforcement_name_old = []
        for i in reinforcement_detail:
            form = SQLFORM(db.reinforcement_used_in_design, i, showid=False, deletable=True)
            design_id = i.design_id
            reinforcement_name_old = db(db.reinforcement.id == i.reinforcement_id).select()
            design_name = db(db.design.id == i.design_id).select()
        if form.process().accepted:
            values = db(db.reinforcement_values.reinforcement_used_in_design_id == reinforcement_detail_id).select()
            reinforcement_name = db(db.reinforcement.id == form.vars.reinforcement_id).select()
            if request.vars.delete_this_record:
                for value in values:
                    value.delete_record()

                #Reducing Cost
                product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
                for product in product_quotation_table:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    product.reinforcement_cost -= float(Infix(convert(form.vars.cost_calculation,parameter_value)))
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted reinforcement details name: ' + reinforcement_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:
                for value in values:
                    try:
                        parameter_values_table = db(db.design_parameters_values.product_id == value.product_id).select(orderby=db.design_parameters_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.quantity = form.vars.quantity
                        value.length_value = Infix(convert(form.vars.length_calculation,parameter_value))
                        value.reinforcement_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                try:
                    #Updating Cost
                    product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
                    for product in product_quotation_table:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))
                        product.reinforcement_cost -= float(Infix(convert(reinforcement_detail[0].cost_calculation,parameter_value)))
                        product.reinforcement_cost += float(Infix(convert(form.vars.cost_calculation,parameter_value)))
                        profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                        product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                        product.total_value = product.total_value*product.quantity
                        product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                        product.total_value_per_piece = product.final_value/product.quantity
                        product.update_record()
                except:
                    pass
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated reinforcement details name: ' + reinforcement_name_old[0].name
                               + ' quantity: ' + str(reinforcement_detail[0].quantity)
                                + ' length_calculation: ' + reinforcement_detail[0].length_calculation + ' cost_calculation: ' + reinforcement_detail[0].cost_calculation + ' to ' + 'name: ' + reinforcement_name[0].name
                                + ' quantity: ' + str(form.vars.quantity)
                                + ' length_calculation: ' + form.vars.length_calculation + ' cost_calculation: ' + form.vars.cost_calculation + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_reinforcement_detail():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.reinforcement_used_in_design.design_id.default = design_id
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.reinforcement_used_in_design)
        if form.process().accepted:
            reinforcement_name = db(db.reinforcement.id == form.vars.reinforcement_id).select()
            product_table = db(db.product.design_id == design_id).select()
            product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
            for product in product_table:
                try:
                    parameter_values_table = db(db.design_parameters_values.product_id == product.id).select(orderby=db.design_parameters_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    quantity = form.vars.quantity
                    length_value = Infix(convert(form.vars.length_calculation,parameter_value))
                    reinforcement_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.reinforcement_values.insert(product_id = product.id, reinforcement_used_in_design_id = form.vars.id, length_value = length_value, quantity = quantity, reinforcement_cost = reinforcement_cost)
                except:
                    pass
            for product in product_quotation_table:
                try:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    #Increasing Cost
                    reinforcement_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    product.reinforcement_cost += float(reinforcement_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                except:
                    pass
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted reinforcement details name: ' + reinforcement_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_HAA_detail():
    if auth.user.IS_ADMIN:
        HAA_detail_id = request.args(0,cast=int)
        HAA_detail = db(db.hardware_and_accessories_used_in_design.id == HAA_detail_id).select()
        form = []
        design_id = None
        design_name = []
        HAA_name_old = []
        for i in HAA_detail:
            form = SQLFORM(db.hardware_and_accessories_used_in_design, i, showid=False, deletable=True)
            design_id = i.design_id
            HAA_name_old = db(db.hardware_and_accessories.id == i.hardware_and_accessories_id).select()
            design_name = db(db.design.id == i.design_id).select()

        values2_old = db(db.product_quotation_hardware_values.hardware_and_accessories_used_in_design_id == HAA_detail_id).select()
        if form.process().accepted:
            values = db(db.hardware_and_accessories_values.hardware_and_accessories_used_in_design_id == HAA_detail_id).select()
            values2 = db(db.product_quotation_hardware_values.hardware_and_accessories_used_in_design_id == HAA_detail_id).select()
            HAA_name = db(db.hardware_and_accessories.id == form.vars.hardware_and_accessories_id).select()
            if request.vars.delete_this_record:
                for value in values:
                    value.delete_record()
                for value in values2:
                    value.delete_record()
                for value in values2_old:
                    #Reducing Cost
                    product = db(db.product_in_quotation.id == value.product_in_quotation_id).select()[0]
                    product.hardware_and_accessories_cost -= float(value.hardware_and_accessories_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted hardware details name: ' + HAA_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:
                for value in values:
                    try:
                        parameter_values_table = db(db.design_parameters_values.product_id == value.product_id).select(orderby=db.design_parameters_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.quantity = form.vars.quantity
                        value.hardware_and_accessories_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                for value in values2:
                    try:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == value.product_in_quotation_id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.quantity = form.vars.quantity
                        old_value = value.hardware_and_accessories_cost
                        value.hardware_and_accessories_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()

                        #Updating Cost
                        product = db(db.product_in_quotation.id == value.product_in_quotation_id).select()[0]
                        product.hardware_and_accessories_cost -= float(old_value)
                        product.hardware_and_accessories_cost += float(value.hardware_and_accessories_cost)
                        profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                        product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                        product.total_value = product.total_value*product.quantity
                        product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                        product.total_value_per_piece = product.final_value/product.quantity
                        product.update_record()
                    except:
                        pass
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated hardware details name: ' + HAA_name_old[0].name
                               + ' quantity: ' + str(HAA_detail[0].quantity)
                                + ' cost_calculation: ' + HAA_detail[0].cost_calculation + ' to ' + 'name: ' + HAA_name[0].name
                                + ' quantity: ' + str(form.vars.quantity)
                                + ' cost_calculation: ' + form.vars.cost_calculation + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_HAA_detail():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.hardware_and_accessories_used_in_design.design_id.default = design_id
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.hardware_and_accessories_used_in_design)
        if form.process().accepted:
            HAA_name = db(db.hardware_and_accessories.id == form.vars.hardware_and_accessories_id).select()
            product_table = db(db.product.design_id == design_id).select()
            product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
            for product in product_table:
                try:
                    parameter_values_table = db(db.design_parameters_values.product_id == product.id).select(orderby=db.design_parameters_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    quantity = form.vars.quantity
                    hardware_and_accessories_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.hardware_and_accessories_values.insert(product_id = product.id, hardware_and_accessories_used_in_design_id = form.vars.id, quantity = quantity, hardware_and_accessories_cost = hardware_and_accessories_cost)
                except:
                    pass
            for product in product_quotation_table:
                try:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    quantity = form.vars.quantity
                    hardware_and_accessories_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.product_quotation_hardware_values.insert(product_in_quotation_id = product.id, hardware_and_accessories_used_in_design_id = form.vars.id, quantity = quantity, hardware_and_accessories_cost = hardware_and_accessories_cost)

                    #Increasing Cost
                    product.hardware_and_accessories_cost += float(hardware_and_accessories_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                except:
                    pass
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted hardware details name: ' + HAA_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_glass_detail():
    if auth.user.IS_ADMIN:
        glass_detail_id = request.args(0,cast=int)
        glass_detail = db(db.glass_used_in_design.id == glass_detail_id).select()
        form = []
        design_id = None
        design_name = []
        glass_name_old = []
        for i in glass_detail:
            form = SQLFORM(db.glass_used_in_design, i, showid=False, deletable=True)
            design_id = i.design_id
            glass_name_old = db(db.glass.id == i.glass_id).select()
            design_name = db(db.design.id == i.design_id).select()
        values2_old = db(db.product_quotation_glass_values.glass_used_in_design_id == glass_detail_id).select()
        if form.process().accepted:
            values = db(db.glass_values.glass_used_in_design_id == glass_detail_id).select()
            values2 = db(db.product_quotation_glass_values.glass_used_in_design_id == glass_detail_id).select()
            glass_name = db(db.glass.id == form.vars.glass_id).select()
            if request.vars.delete_this_record:
                for value in values:
                    value.delete_record()
                for value in values2:
                    value.delete_record()
                for value in values2_old:
                    #Reducing Cost
                    product = db(db.product_in_quotation.id == value.product_in_quotation_id).select()[0]
                    product.glass_cost -= float(value.glass_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                    value.delete_record()
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted glass details name: ' + glass_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:
                for value in values:
                    try:
                        parameter_values_table = db(db.design_parameters_values.product_id == value.product_id).select(orderby=db.design_parameters_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.width = Infix(convert(form.vars.width_calculation,parameter_value))
                        value.height = Infix(convert(form.vars.height_calculation,parameter_value))
                        value.quantity = form.vars.quantity
                        value.glass_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                for value in values2:
                    try:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == value.product_in_quotation_id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.width = Infix(convert(form.vars.width_calculation,parameter_value))
                        value.height = Infix(convert(form.vars.height_calculation,parameter_value))
                        value.quantity = form.vars.quantity
                        old_value = value.glass_cost
                        value.glass_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()

                        #Updating Cost
                        product = db(db.product_in_quotation.id == value.product_in_quotation_id).select()[0]
                        product.glass_cost -= old_value
                        product.glass_cost += float(value.glass_cost)
                        profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                        product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                        product.total_value = product.total_value*product.quantity
                        product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                        product.total_value_per_piece = product.final_value/product.quantity
                        product.update_record()
                    except:
                        pass
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated glass details name: ' + glass_name_old[0].name
                               + ' width_calculation: ' + str(glass_detail[0].width_calculation) + ' height_calculation: ' + str(glass_detail[0].height_calculation) + ' quantity: ' + str(glass_detail[0].quantity)
                                + ' cost_calculation: ' + glass_detail[0].cost_calculation + ' to ' + 'name: ' + glass_name[0].name
                                + ' width_calculation: ' + str(form.vars.width_calculation) + ' height_calculation: ' + str(form.vars.height_calculation) + ' quantity: ' + str(form.vars.quantity)
                                + ' cost_calculation: ' + form.vars.cost_calculation + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_glass_detail():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.glass_used_in_design.design_id.default = design_id
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.glass_used_in_design)
        if form.process().accepted:
            glass_name = db(db.glass.id == form.vars.glass_id).select()
            product_table = db(db.product.design_id == design_id).select()
            product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
            for product in product_table:
                try:
                    parameter_values_table = db(db.design_parameters_values.product_id == product.id).select(orderby=db.design_parameters_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    width = Infix(convert(form.vars.width_calculation,parameter_value))
                    height = Infix(convert(form.vars.height_calculation,parameter_value))
                    quantity = form.vars.quantity
                    glass_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.glass_values.insert(product_id = product.id, glass_used_in_design_id = form.vars.id, width = width, height = height, quantity = quantity, glass_cost = glass_cost)
                except:
                    pass
            for product in product_quotation_table:
                try:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    width = Infix(convert(form.vars.width_calculation,parameter_value))
                    height = Infix(convert(form.vars.height_calculation,parameter_value))
                    quantity = form.vars.quantity
                    glass_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.product_quotation_glass_values.insert(product_in_quotation_id = product.id, glass_used_in_design_id = form.vars.id, width = width, height = height, quantity = quantity, glass_cost = glass_cost)

                    #Increasing Cost
                    product.glass_cost += float(glass_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                except:
                    pass
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted glass details name: ' + glass_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_material_detail():
    if auth.user.IS_ADMIN:
        material_detail_id = request.args(0,cast=int)
        material_detail = db(db.installation_material_used_in_design.id == material_detail_id).select()
        form = []
        design_id = None
        design_name = []
        material_name_old = []
        for i in material_detail:
            form = SQLFORM(db.installation_material_used_in_design, i, showid=False, deletable=True)
            design_id = i.design_id
            material_name_old = db(db.installation_material.id == i.installation_material_id).select()
            design_name = db(db.design.id == i.design_id).select()
        if form.process().accepted:
            values = db(db.installation_material_values.installation_material_used_in_design_id == material_detail_id).select()
            material_name = db(db.installation_material.id == form.vars.installation_material_id).select()
            if request.vars.delete_this_record:
                for value in values:
                    value.delete_record()

                #Reducing Cost
                product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
                for product in product_quotation_table:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    product.installation_material_cost -= float(Infix(convert(form.vars.cost_calculation,parameter_value)))
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted installation material details name: ' + material_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:
                for value in values:
                    try:
                        parameter_values_table = db(db.design_parameters_values.product_id == value.product_id).select(orderby=db.design_parameters_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        value.quantity = form.vars.quantity
                        value.installation_material_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                try:
                    #Updating Cost
                    product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
                    for product in product_quotation_table:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))
                        product.installation_material_cost -= float(Infix(convert(material_detail[0].cost_calculation,parameter_value)))
                        product.installation_material_cost += float(Infix(convert(form.vars.cost_calculation,parameter_value)))
                        profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                        product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                        product.total_value = product.total_value*product.quantity
                        product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                        product.total_value_per_piece = product.final_value/product.quantity
                        product.update_record()
                except:
                    pass
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated installation material details name: ' + material_name_old[0].name
                               + ' quantity: ' + str(material_detail[0].quantity)
                                + ' cost_calculation: ' + material_detail[0].cost_calculation + ' to ' + 'name: ' + material_name[0].name
                                + ' quantity: ' + str(form.vars.quantity)
                                + ' cost_calculation: ' + form.vars.cost_calculation + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_material_detail():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.installation_material_used_in_design.design_id.default = design_id
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.installation_material_used_in_design)
        if form.process().accepted:
            material_name = db(db.installation_material.id == form.vars.installation_material_id).select()
            product_table = db(db.product.design_id == design_id).select()
            product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
            for product in product_table:
                try:
                    parameter_values_table = db(db.design_parameters_values.product_id == product.id).select(orderby=db.design_parameters_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))
                    quantity = form.vars.quantity
                    installation_material_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    db.installation_material_values.insert(product_id = product.id, installation_material_used_in_design_id = form.vars.id, quantity = quantity, installation_material_cost = installation_material_cost)
                except:
                    pass
            for product in product_quotation_table:
                try:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    #Increasing Cost
                    installation_material_cost = Infix(convert(form.vars.cost_calculation,parameter_value))
                    product.installation_material_cost += float(installation_material_cost)
                    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
                    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
                    product.total_value = product.total_value*product.quantity
                    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
                    product.total_value_per_piece = product.final_value/product.quantity
                    product.update_record()
                except:
                    pass
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted installation material details name: ' + material_name[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def update_extra_information():
    if auth.user.IS_ADMIN:
        extra_information_detail_id = request.args(0,cast=int)
        extra_information_detail = db(db.extra_information_in_design.id == extra_information_detail_id).select()
        form = []
        design_id = None
        design_name = []
        for i in extra_information_detail:
            form = SQLFORM(db.extra_information_in_design, i, showid=False, deletable=True)
            design_id = i.design_id
            design_name = db(db.design.id == i.design_id).select()
        if form.process().accepted:
            values = db(db.extra_information_values.extra_information_in_design_id == extra_information_detail_id).select()
            values2 = db(db.product_quotation_extra_information_values.extra_information_in_design_id == extra_information_detail_id).select()
            if request.vars.delete_this_record:
                for value in values:
                    value.delete_record()
                for value in values2:
                    value.delete_record()
                    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' deleted extra information name: ' + extra_information_detail[0].name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            else:
                for value in values:
                    try:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == value.product_in_quotation_id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        if form.vars.default_value:
                            value.default_value = form.vars.default_value
                        elif form.vars.calculation:
                            value.extra_information_value = Infix(convert(form.vars.calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                for value in values2:
                    try:
                        parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == value.product_in_quotation_id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                        parameter_value = []
                        for i in parameter_values_table:
                            parameter_value.append(str(i.parameter_value))

                        if form.vars.default_value:
                            value.default_value = form.vars.default_value
                        elif form.vars.calculation:
                            value.extra_information_value = Infix(convert(form.vars.calculation,parameter_value))
                        value.update_record()
                    except:
                        pass
                db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated extra_information name: ' + extra_information_detail[0].name
                               + ' default value: ' + str(extra_information_detail[0].default_value)
                                + ' calculation: ' + extra_information_detail[0].calculation + ' to ' + 'name: ' + form.vars.name
                                + ' default_value: ' + str(form.vars.default_value)
                                + ' calculation: ' + form.vars.calculation + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            response.flash='Form accepted'
            redirect(URL('view_design', args=design_id))
        elif form.errors:
            response.flash='Form has errors'
        else:
            response.flash='Please update'
        return dict(form = form)
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def add_update_extra_information():
    if auth.user.IS_ADMIN:
        design_id = request.args(0,cast=int)
        db.extra_information_in_design.design_id.default = design_id
        design_name = db(db.design.id == design_id).select()
        form = SQLFORM(db.extra_information_in_design)
        if form.process().accepted:
            response.flash = 'form accepted'
            product_table = db(db.product.design_id == design_id).select()
            product_quotation_table = db(db.product_in_quotation.design_id == design_id).select()
            for product in product_table:
                try:
                    parameter_values_table = db(db.design_parameters_values.product_id == product.id).select(orderby=db.design_parameters_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    default_value = None
                    extra_information_value = None
                    if form.vars.default_value != None and form.vars.default_value != '':
                        default_value = form.vars.default_value
                    elif form.vars.calculation != None and form.vars.calculation != '':
                        extra_information_value = Infix(convert(form.vars.calculation,parameter_value))
                    db.extra_information_values.insert(product_id = product.id, extra_information_in_design_id = form.vars.id, default_value = default_value, extra_information_value = extra_information_value)
                except:
                    pass
            for product in product_quotation_table:
                try:
                    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
                    parameter_value = []
                    for i in parameter_values_table:
                        parameter_value.append(str(i.parameter_value))

                    default_value = None
                    extra_information_value = None
                    if form.vars.default_value != None and form.vars.default_value != '':
                        default_value = form.vars.default_value
                    elif form.vars.calculation != None and form.vars.calculation != '':
                        extra_information_value = Infix(convert(form.vars.calculation,parameter_value))
                    db.product_quotation_extra_information_values.insert(product_in_quotation_id = product.id, extra_information_in_design_id = form.vars.id, default_value = default_value, extra_information_value = extra_information_value)
                except:
                    pass
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted extra_information name: ' + form.vars.name + ' in design ' + design_name[0].name, log_time = datetime.datetime.now())
            redirect(URL('view_design.html',args=design_id))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please fill out the form'
        return dict(form=form)
    else:
        response.flash = 'Requires Admin Access'

#------------------------------------------- COPY DESIGN -----------------------------------------#
@auth.requires_login()
def copy_design_details():
    design_id = request.vars.design_id
    design = db(db.design.id == design_id).select()[0]
    return dict(design_id = design_id, design = design)

@auth.requires_login()
def copy_design():
    design_id = request.vars.design_id
    name = request.vars.new_design_name
    design = db(db.design.id == design_id).select()[0]

    parameter = db(db.design_parameters.design_id == design_id).select()
    profile = db(db.profile_used_in_design.design_id == design_id).select()
    reinforcement = db(db.reinforcement_used_in_design.design_id == design_id).select()
    HAA = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select()
    glass = db(db.glass_used_in_design.design_id == design_id).select()
    material = db(db.installation_material_used_in_design.design_id == design_id).select()
    extra_info = db(db.extra_information_in_design.design_id == design_id).select()

    #Copying Values
    new_id = db.design.insert(name = name, description = design.description, design_image = design.design_image)

    for entry in parameter:
        db.design_parameters.insert(design_id = new_id, name = entry.name, codename = entry.codename)
    for entry in profile:
        db.profile_used_in_design.insert(design_id = new_id, profile_id = entry.profile_id, profile_position = entry.profile_position,
                                 cut = entry.cut, length_calculation = entry.length_calculation, quantity = entry.quantity, cost_calculation = entry.cost_calculation)
    for entry in reinforcement:
        db.reinforcement_used_in_design.insert(design_id = new_id, reinforcement_id = entry.reinforcement_id, length_calculation = entry.length_calculation, quantity = entry.quantity, cost_calculation = entry.cost_calculation)
    for entry in HAA:
        db.hardware_and_accessories_used_in_design.insert(design_id = new_id, hardware_and_accessories_id = entry.hardware_and_accessories_id, quantity = entry.quantity, cost_calculation = entry.cost_calculation)
    for entry in glass:
        db.glass_used_in_design.insert(design_id = new_id, glass_id = entry.glass_id, width_calculation = entry.width_calculation, height_calculation = entry.height_calculation, quantity = entry.quantity, cost_calculation = entry.cost_calculation)
    for entry in material:
        db.installation_material_used_in_design.insert(design_id = new_id, installation_material_id = entry.installation_material_id, quantity = entry.quantity, cost_calculation = entry.cost_calculation)
    for entry in extra_info:
        db.extra_information_in_design.insert(design_id = new_id, name = entry.name, default_value = entry.default_value, calculation = entry.calculation)

    redirect(URL('admin_functions.html'))
    return dict()

#endregion

#region Others
#-------------------------------------------- GIVE APPROVAL/VIEW LOGS -----------------------------------------#
@auth.requires_login()
def give_approval():
    if auth.user.IS_ADMIN:
        user_table = db((db.auth_user.id >= 0) & (db.auth_user.registration_key != '')).select()
        return dict(user_table = user_table)
    else:
        response.flash = 'Requires Admin Access'
@auth.requires_login()
def give_approval_helper():
    if auth.user.IS_ADMIN:
        approved = []
        for var in request.vars:
            try:
                approved.append(int(var))
            except:
                pass
        approving_users = db((db.auth_user. id >= 0) & (db.auth_user.id.belongs(approved))).select()
        for user in approving_users:
            user.registration_key = ''
            user.update_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' gave approval to ' + user.first_name + ' ' + user.last_name, log_time = datetime.datetime.now())
        response.flash = 'Success'
        redirect('admin_functions.html')
        return dict()
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def get_logtime():
    if auth.user.IS_ADMIN:
        return dict()
    else:
        response.flash = 'Requires Admin Access'

@auth.requires_login()
def view_logs():
    if auth.user.IS_ADMIN:
        time = request.vars.time
        from_time = request.vars.from_time
        to_time = request.vars.to_time
        month = 365/12
        log_table = db(db.logs.id >= 0).select(orderby=~db.logs.log_time)
        if time == '1':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today() - datetime.timedelta(days=1))).select(orderby=~db.logs.log_time)
        elif time == '3':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today() - datetime.timedelta(days=3))).select(orderby=~db.logs.log_time)
        elif time == '7':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today() - datetime.timedelta(days=7))).select(orderby=~db.logs.log_time)
        elif time == '14':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today() - datetime.timedelta(days=14))).select(orderby=~db.logs.log_time)
        elif time == '30':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today().replace(month = datetime.date.today().month - 1))).select(orderby=~db.logs.log_time)
        elif time == '90':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today().replace(month = datetime.date.today().month - 3))).select(orderby=~db.logs.log_time)
        elif time == '180':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today().replace(month = datetime.date.today().month - 6))).select(orderby=~db.logs.log_time)
        elif time == '365':
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= datetime.date.today().replace(year = datetime.date.today().year - 1))).select(orderby=~db.logs.log_time)
        elif time == 'picked':
            from_time = datetime.datetime.strptime(from_time,'%Y-%m-%d').date()
            to_time = datetime.datetime.strptime(to_time,'%Y-%m-%d').date()
            to_time = to_time.replace(day = to_time.day + 1)
            log_table = db((db.logs.id >= 0) & (db.logs.log_time >= from_time) & (db.logs.log_time <= to_time)).select(orderby=~db.logs.log_time)
        return dict(log_table = log_table)
    else:
        response.flash = 'Requires Admin Access'
#endregion

#endregion

#region Inventory Management
#############################################################################################################
#---------------------------------------- INVENTORY MANAGEMENT ---------------------------------------------#
#############################################################################################################
@auth.requires_login()
def inventory_management():
    profile_table = db(db.profile.id >= 0).select()
    reinforcement_table = db(db.reinforcement.id >= 0).select()
    HAA_table = db(db.hardware_and_accessories.id >= 0).select()
    glass_table = db(db.glass.id >= 0).select()
    material_table = db(db.installation_material.id >= 0).select()
    return dict(profile_table = profile_table,reinforcement_table = reinforcement_table,
                HAA_table = HAA_table, glass_table = glass_table, material_table = material_table)

#region Profile
#---------------------------------------- ADD/DELETE/UPDATE PROFILE ---------------------------------------------#
@auth.requires_login()
def add_profile_entry():
    form = SQLFORM(db.profile)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted profile entry ' + form.vars.name + ' ---- ' + form.vars.quantity, log_time = datetime.datetime.now())
        redirect(URL('inventory_management.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def update_profile_entry():
    entry_id = request.vars.entry_id
    l = db(db.profile.id == entry_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_code = i.profile_code
        old_weight = i.weight
        old_length = i.profile_length
        old_number = i.number_of_pieces
        old_price = i.price
        old_quantity = i.quantity
        form = SQLFORM(db.profile, i, deletable=True)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated profile entry name: ' + old_name + ' code: ' +
                            str(old_code) + ' weight: ' + str(old_weight) + ' length: ' + str(old_length) + ' number of pieces: ' + str(old_number) +
                            ' price: ' + str(old_price) + ' quantity: ' + str(old_quantity) +
                            ' to ' + form.vars.name + ' ' + str(form.vars.profile_code) + ' ' + str(form.vars.weight) + ' ' + str(form.vars.profile_length)
                + ' ' + str(form.vars.number_of_pieces) + ' ' + str(form.vars.price) + ' ' + str(form.vars.quantity),log_time=datetime.datetime.now())
            redirect(URL('inventory_management.html'))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please update'
    return dict(form=form)
@auth.requires_login()
def update_profile_helper():
    entry_id = request.vars.entry_id
    quantity = request.vars.quantity
    row=db.profile(db.profile.id==entry_id)
    old_quantity=row.quantity
    if request.vars.Add:
        row.quantity=int(row.quantity)+int(quantity)
    elif request.vars.Delete:
        row.quantity=int(row.quantity)-int(quantity)
    row.update_record()
    db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated quantity entry of ' + str(row.name) + ' from ' + str(old_quantity)
                            + ' to ' + str(row.quantity),
                log_time=datetime.datetime.now())
    redirect(URL('inventory_management.html'))
    return dict()

"""@auth.requires_login()
def remove_profile():
    profile_table = db(db.profile.id >= 0).select()
    return dict(profile_table = profile_table)
@auth.requires_login()
def remove_profile_helper():
    if auth.user.IS_ADMIN:
        profile_list = []
        for var in request.vars:
            try:
                profile_list.append(int(var))
            except:
                pass
        new_profile_list = db((db.profile.id >= 0) & (db.profile.id.belongs(profile_list))).select()
        for profile in new_profile_list:
            profile.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed profile entry ' + profile.name , log_time = datetime.datetime.now())
        redirect('inventory_management.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'
"""
#endregion

#region Reinforcement
#---------------------------------------- ADD/DELETE/UPDATE REINFORCEMENT ---------------------------------------------#
@auth.requires_login()
def add_reinforcement_entry():
    form = SQLFORM(db.reinforcement)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted entry ' + form.vars.name + ' ---- ' + form.vars.quantity, log_time = datetime.datetime.now())
        redirect(URL('inventory_management.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def update_reinforcement_entry():
    entry_id = request.vars.entry_id
    l = db(db.reinforcement.id == entry_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_desc = i.description
        old_weight = i.weight
        old_length = i.reinforcement_length
        old_number = i.number_of_pieces
        old_price = i.price
        old_quantity = i.quantity
        form = SQLFORM(db.reinforcement, i, deletable=True)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated reinforcement entry name: ' + old_name + ' description: ' +
                            str(old_desc) + ' weight: ' + str(old_weight) + ' length: ' + str(old_length) + ' number of pieces: ' + str(old_number) +
                            ' price: ' + str(old_price) + ' quantity: ' + str(old_quantity) +
                            ' to ' + form.vars.name + ' ' + str(form.vars.description) + ' ' + str(form.vars.weight) + ' ' + str(form.vars.profile_length)
                + ' ' + str(form.vars.number_of_pieces) + ' ' + str(form.vars.price) + ' ' + str(form.vars.quantity),log_time=datetime.datetime.now())
            redirect(URL('inventory_management.html'))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please update'
    return dict(form=form)
@auth.requires_login()
def update_reinforcement_helper():
    entry_id = request.vars.entry_id
    quantity = request.vars.quantity
    row=db.reinforcement(db.reinforcement.id==entry_id)
    old_quantity=row.quantity

    if request.vars.Add:
        row.quantity=int(row.quantity)+int(quantity)
    elif request.vars.Delete:
        row.quantity=int(row.quantity)-int(quantity)
    row.update_record()
    db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated quantity entry ' + str(old_quantity)
                            + ' to ' + str(row.quantity),
                log_time=datetime.datetime.now())
    redirect(URL('inventory_management.html'))
    return dict()

"""@auth.requires_login()
def remove_reinforcement():
    reinforcement_table = db(db.reinforcement.id >= 0).select()
    return dict(reinforcement_table = reinforcement_table)
@auth.requires_login()
def remove_reinforcement_helper():
    if auth.user.IS_ADMIN:
        reinforcement_list = []
        for var in request.vars:
            try:
                reinforcement_list.append(int(var))
            except:
                pass
        new_reinforcement_list = db((db.reinforcement.id >= 0) & (db.reinforcement.id.belongs(reinforcement_list))).select()
        for reinforcement in new_reinforcement_list:
            reinforcement.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed reinforcement ' + reinforcement.name , log_time = datetime.datetime.now())
        redirect('inventory_management.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'
"""
#endregion

#region Hardware
#---------------------------------------- ADD/DELETE/UPDATE HARDWARE ---------------------------------------------#
@auth.requires_login()
def add_HAA_entry():
    form = SQLFORM(db.hardware_and_accessories)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted entry ' + form.vars.name + ' ---- ' + form.vars.quantity, log_time = datetime.datetime.now())
        redirect(URL('inventory_management.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def update_HAA_entry():
    entry_id = request.vars.entry_id
    l = db(db.hardware_and_accessories.id == entry_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_desc = i.description
        old_price = i.price
        old_quantity = i.quantity
        form = SQLFORM(db.hardware_and_accessories, i, deletable=True)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated hardware and accessories entry name: ' + old_name + ' description: ' +
                            str(old_desc) + ' price: ' + str(old_price) + ' quantity: ' + str(old_quantity) +
                            ' to ' + form.vars.name + ' ' + str(form.vars.description) + ' ' + str(form.vars.price) + ' ' + str(form.vars.quantity),
                log_time=datetime.datetime.now())
            redirect(URL('inventory_management.html'))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please update'
    return dict(form=form)
@auth.requires_login()
def update_HAA_helper():
    entry_id = request.vars.entry_id
    quantity = request.vars.quantity
    row=db.hardware_and_accessories(db.hardware_and_accessories.id==entry_id)
    old_quantity=row.quantity

    if request.vars.Add:
        row.quantity=int(row.quantity)+int(quantity)
    elif request.vars.Delete:
        row.quantity=int(row.quantity)-int(quantity)
    row.update_record()
    db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated quantity entry ' + str(old_quantity)
                            + ' to ' + str(row.quantity),
                log_time=datetime.datetime.now())
    redirect(URL('inventory_management.html'))
    return dict()

"""@auth.requires_login()
def remove_HAA():
    HAA_table = db(db.hardware_and_accessories.id >= 0).select()
    return dict(HAA_table = HAA_table)
@auth.requires_login()
def remove_HAA_helper():
    if auth.user.IS_ADMIN:
        HAA_list = []
        for var in request.vars:
            try:
                HAA_list.append(int(var))
            except:
                pass
        new_HAA_list = db((db.hardware_and_accessories.id >= 0) & (db.hardware_and_accessories.id.belongs(HAA_list))).select()
        for HAA in new_HAA_list:
            HAA.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed hardware_and_accessories ' + hardware_and_accessories.name , log_time = datetime.datetime.now())
        redirect('inventory_management.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'
"""
#endregion

#region Glass
#---------------------------------------- ADD/DELETE/UPDATE GLASS ---------------------------------------------#
@auth.requires_login()
def add_glass_entry():
    form = SQLFORM(db.glass)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted entry ' + form.vars.name + ' ---- ' + form.vars.quantity, log_time = datetime.datetime.now())
        redirect(URL('inventory_management.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def update_glass_entry():
    entry_id = request.vars.entry_id
    l = db(db.glass.id == entry_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_quantity = i.quantity
        form = SQLFORM(db.glass, i, deletable=True)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated hardware and accessories entry name: ' + old_name + ' description: ' +
                            str(old_desc) + ' price: ' + str(old_price) + ' quantity: ' + str(old_quantity) +
                            ' to ' + form.vars.name + ' ' + str(form.vars.description) + ' ' + str(form.vars.price) + ' ' + str(form.vars.quantity),
                log_time=datetime.datetime.now())
            redirect(URL('inventory_management.html'))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please update'
    return dict(form=form)
@auth.requires_login()
def update_glass_helper():
    entry_id = request.vars.entry_id
    quantity = request.vars.quantity
    row=db.glass(db.glass.id==entry_id)
    old_quantity=row.quantity

    if request.vars.Add:
        row.quantity=int(row.quantity)+int(quantity)
    elif request.vars.Delete:
        row.quantity=int(row.quantity)-int(quantity)
    row.update_record()
    db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated quantity entry ' + str(old_quantity)
                            + ' to ' + str(row.quantity),
                log_time=datetime.datetime.now())
    redirect(URL('inventory_management.html'))
    return dict()

"""@auth.requires_login()
def remove_glass():
    glass_table = db(db.glass.id >= 0).select()
    return dict(glass_table = glass_table)
@auth.requires_login()
def remove_glass_helper():
    if auth.user.IS_ADMIN:
        glass_list = []
        for var in request.vars:
            try:
                glass_list.append(int(var))
            except:
                pass
        new_glass_list = db((db.glass.id >= 0) & (db.glass.id.belongs(glass_list))).select()
        for glass in new_glass_list:
            glass.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed glass ' + glass.name , log_time = datetime.datetime.now())
        redirect('inventory_management.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'
"""
#endregion

#region Installation Material
#---------------------------------------- ADD/DELETE/UPDATE INSTALLATION MATERIAL ---------------------------------------------#
@auth.requires_login()
def add_material_entry():
    form = SQLFORM(db.installation_material)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted entry ' + form.vars.name + ' ---- ' + form.vars.quantity, log_time = datetime.datetime.now())
        redirect(URL('inventory_management.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def update_material_entry():
    entry_id = request.vars.entry_id
    l = db(db.installation_material.id == entry_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_quantity = i.quantity
        form = SQLFORM(db.installation_material, i, deletable=True)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated hardware and accessories entry name: ' + old_name + ' description: ' +
                            str(old_desc) + ' price: ' + str(old_price) + ' quantity: ' + str(old_quantity) +
                            ' to ' + form.vars.name + ' ' + str(form.vars.description) + ' ' + str(form.vars.price) + ' ' + str(form.vars.quantity),
                log_time=datetime.datetime.now())
            redirect(URL('inventory_management.html'))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please update'
    return dict(form=form)
@auth.requires_login()
def update_material_helper():
    entry_id = request.vars.entry_id
    quantity = request.vars.quantity
    row=db.installation_material(db.installation_material.id==entry_id)
    old_quantity=row.quantity

    if request.vars.Add:
        row.quantity=int(row.quantity)+int(quantity)
    elif request.vars.Delete:
        row.quantity=int(row.quantity)-int(quantity)
    row.update_record()
    db.logs.insert(
                log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated quantity entry ' + str(old_quantity)
                            + ' to ' + str(row.quantity),
                log_time=datetime.datetime.now())
    redirect(URL('inventory_management.html'))
    return dict()

"""@auth.requires_login()
def remove_material():
    material_table = db(db.installation_material.id >= 0).select()
    return dict(material_table = material_table)
@auth.requires_login()
def remove_material_helper():
    if auth.user.IS_ADMIN:
        material_list = []
        for var in request.vars:
            try:
                material_list.append(int(var))
            except:
                pass
        new_material_list = db((db.installation_material.id >= 0) & (db.installation_material.id.belongs(material_list))).select()
        for material in new_material_list:
            material.delete_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed installation_material ' + installation_material.name , log_time = datetime.datetime.now())
        redirect('inventory_management.html')
        response.flash = 'Success'
        return dict()
    else:
        response.flash = 'Requires Admin Access'
"""
#endregion

#endregion

#region Project Management
################################################################################################################
#------------------------------------------- PROJECT MANAGEMENT -----------------------------------------------#
################################################################################################################

#region Project
#---------------------------------------- ADD/UPDATE/VIEW/DELETE PROJECT DETAILS ---------------------------------------------#
@auth.requires_login()
def add_new_project():
    org_list = db(db.organization.id >= 0).select()
    form = SQLFORM(db.organization)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted organization entry ' + form.vars.name, log_time = datetime.datetime.now())
        redirect(URL('add_project_details.html', vars=dict(org_id=form.vars.id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(org_list = org_list, form=form)

@auth.requires_login()
def add_project_details():
    org_id = request.vars.org_id
    db.project.organization_id.default = org_id
    db.project.registered_date.default = datetime.date.today()
    form = SQLFORM(db.project,submit_button="Confirm and go to POC details")
    if form.process().accepted:
        response.flash = 'form accepted'
        project_list = db(db.project.id == form.vars.id).select()
        for project in project_list:
            project.name = 'Project_' + str(project.id)
            project.update_record()
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted project entry ' + project.name + " address: " + project.address + " description: " + project.description, log_time = datetime.datetime.now())
        redirect(URL('add_POC_details.html', args = form.vars.id, vars=dict(org_id=org_id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def add_POC_details():
    project_id = request.args(0, cast=int)
    org_id = request.vars.org_id
    project_to_POC_list = db(db.project_to_poc.project_id == project_id).select()
    project_POC_list = []
    for entry in project_to_POC_list:
        temp_list = db(db.point_of_contact.id == entry.poc_id).select()
        for temp in temp_list:
            project_POC_list.append(temp)
    POC_list = db((db.point_of_contact.organization_id == org_id) & ~(db.point_of_contact.id.belongs(project_POC_list))).select()
    db.point_of_contact.organization_id.default = org_id
    form = SQLFORM(db.point_of_contact)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted point of contact entry ' + form.vars.name + " phone number: " + form.vars.phone_number, log_time = datetime.datetime.now())
        redirect(URL('add_POC_helper', args = [project_id, form.vars.id], vars=dict(org_id=org_id,project_id=project_id,POC_id=form.vars.id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(POC_list = POC_list, project_POC_list = project_POC_list, form = form, project_id = project_id, org_id = org_id)
@auth.requires_login()
def add_POC_helper():
    project_id = request.vars.project_id
    POC_id = request.vars.POC_id
    poc_list = db(db.point_of_contact.id == POC_id).select()
    project_list = db(db.project.id == project_id).select()
    org_id = request.vars.org_id
    db.project_to_poc.insert(project_id = project_id, poc_id = POC_id)
    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' added point of contact ' + poc_list[0].name + " phone number: " + poc_list[0].phone_number + " to project " + project_list[0].name, log_time = datetime.datetime.now())
    redirect(URL('add_POC_details',args=project_id, vars=dict(org_id=org_id)))
    return dict()

@auth.requires_login()
def view_project():
    project_id = request.vars.project_id
    project = db(db.project.id == project_id).select()
    org = []
    phase_dict = {'Started':'Production','Production':'Delivery','Delivery':'Installation','Installation':'Completed'}
    design_parameters_vals = {}
    for pro in project:
        org = db(db.organization.id == pro.organization_id).select()
    org_id = org[0].id

    product_list = db(db.product.project_id == project_id).select()
    project_poc_list = db(db.project_to_poc.project_id == project_id).select()
    POC_list = []
    for entry in project_poc_list:
        temp_list = db(db.point_of_contact.id == entry.poc_id).select()
        for temp in temp_list:
            POC_list.append(temp)

    for product in product_list:
        temp = db(db.design_parameters_values.product_id == product.id).select()
        design_parameters_vals[product.id] = []
        for val in temp:
            design_parameters_vals[product.id].append(str(val.parameter_value))
    return dict(project = project, product_list = product_list, POC_list = POC_list, project_id = project_id, org = org, org_id = org_id,phase_dict = phase_dict, design_parameters_vals = design_parameters_vals)

@auth.requires_login()
def update_project():
    project_id = request.vars.project_id
    l = db(db.project.id == project_id).select()
    for i in l:
        form = SQLFORM(db.project, i, deletable=False, showid=False)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated details of project Name: ' + i.name + ' Description: ' + i.description + ' Address: ' + i.address + ' Phase: ' + i.phase + ' to Description: ' + form.vars.description + ' Address: ' + form.vars.address + ' Phase: ' + form.vars.phase, log_time = datetime.datetime.now())
            redirect(URL('view_project.html',vars = dict(project_id = project_id)))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please update'
    return dict(form=form)

@auth.requires_login()
def update_POC_details():
    entry_id = request.vars.entry_id
    project_id = request.vars.project_id
    l=db(db.point_of_contact.id==entry_id).select()
    form=[]
    for i in l:
        form = SQLFORM(db.point_of_contact, i, deletable=False, showid=False)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated point of contact Name: ' + old_name + ' Phone Number: ' + old_number + ' Email: ' + old_email + ' Designation: ' + old_designation +
                                       ' to Name: ' + form.vars.name + + ' Phone Number: ' + form.vars.phone_number + ' Email: ' + form.vars.email + ' Designation: ' + form.vars.designation, log_time = datetime.datetime.now())
            redirect(URL('view_project.html', vars=dict(project_id = project_id)))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please update'
    return dict(form=form)

@auth.requires_login()
def link_POC():
    redirect(URL('add_POC_details', args = request.vars.project_id, vars = dict(org_id = request.vars.org_id)))
    return dict()

@auth.requires_login()
def unlink_POC():
    project_id = request.vars.project_id
    project_poc_list = db(db.project_to_poc.project_id == project_id).select()
    POC_list = []
    for entry in project_poc_list:
        temp_list = db(db.point_of_contact.id == entry.poc_id).select()
        for temp in temp_list:
            POC_list.append(temp)
    return dict(POC_list = POC_list, project_id = project_id)
@auth.requires_login()
def unlink_POC_helper():
    project_id = request.vars.project_id
    project = db(db.project.id == project_id).select()
    POC_list = []
    for var in request.vars:
        try:
            POC_list.append(int(var))
        except:
            pass
    unlink_list = db((db.project_to_poc.project_id == project_id) & (db.project_to_poc.poc_id.belongs(POC_list))).select()
    for user in unlink_list:
        username = db(db.point_of_contact.id == user.poc_id).select()[0].name
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' unlinked point of contact ' + username + ' from project ' + project[0].name, log_time = datetime.datetime.now())
        user.delete_record()
    redirect(URL('view_project.html', vars=dict(project_id = project_id)))
    response.flash = 'Success'
    return dict()

@auth.requires_login()
def upload_completion_letter():
    project_id = request.vars.project_id
    db.documents.project_id.default = project_id
    db.documents.upload_time.default = datetime.datetime.now()
    db.documents.document_type.default = 'Completion Letter'
    letters = db((db.documents.project_id == project_id) & (db.documents.document_type == 'Completion Letter')).select()
    db.documents.name.default = 'Completion Letter_' + str(len(letters)+1)
    db.documents.document_type.writable = False
    form = SQLFORM(db.documents)
    project = db(db.project.id == project_id).select()
    project_name = project[0].name
    project[0].update_record(phase = 'Completed')
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' uploaded Completion Letter ' + ' with Name: ' + form.vars.name + ' of project ' + project_name, log_time = datetime.datetime.now())
        redirect(URL('view_project.html',vars=dict(project_id = project_id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def upload_other_documents():
    project_id = request.vars.project_id
    db.documents.project_id.default = project_id
    db.documents.upload_time.default = datetime.datetime.now()
    db.documents.document_type.default = 'Other'
    letters = db((db.documents.project_id == project_id) & (db.documents.document_type == 'Other')).select()
    db.documents.name.default = 'Other_' + str(len(letters)+1)
    db.documents.document_type.writable = False
    form = SQLFORM(db.documents)
    project = db(db.project.id == project_id).select()
    project_name = project[0].name
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' uploaded Other ' + ' document ' + ' with Name: ' + form.vars.name + ' of project ' + project_name, log_time = datetime.datetime.now())
        redirect(URL('view_project.html',vars=dict(project_id = project_id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def view_docs():
    project_id = request.vars.project_id
    documents = db(db.documents.project_id == project_id).select()
    for entry in documents:
        if entry.document_file == None:
            entry.delete_record()
    documents = db(db.documents.project_id == project_id).select()
    return dict(documents = documents, project_id = project_id)

@auth.requires_login()
def delete_project():
    project_list = db(db.project.id >= 0).select()
    return dict(project_list = project_list)

@auth.requires_login()
def delete_project_helper():
    project_list = []
    for var in request.vars:
        try:
            project_list.append(int(var))
        except:
            pass
    delete_list = db((db.project.id >= 0) & (db.project.id.belongs(project_list))).select()
    for project in delete_list:

        #Deleting Project to POC Links
        project_to_user_list = db(db.project_to_poc.project_id == project.id).select()
        for entry in project_to_user_list:
            entry.delete_record()

        #Deleting Documents and associated entries
        document_list = db(db.documents.project_id == project.id).select()
        for entry in document_list:

            quotation_product_list = db(db.product_in_quotation.document_id == entry.id).select()
            for product in quotation_product_list:

                product_quotation_parameter_values_list = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select()
                for parameter in product_quotation_parameter_values_list:
                    parameter.delete_record()

                product_quotation_glass_values_list = db(db.product_quotation_glass_values.product_in_quotation_id == product.id).select()
                for glass in product_quotation_glass_values_list:
                    glass.delete_record()

                product_quotation_hardware_values_list = db(db.product_quotation_hardware_values.product_in_quotation_id == product.id).select()
                for hardware in product_quotation_hardware_values_list:
                    hardware.delete_record()

                product_quotation_extra_information_values_list = db(db.product_quotation_extra_information_values.product_in_quotation_id == product.id).select()
                for info in product_quotation_extra_information_values_list:
                    info.delete_record()

                parameter_table = db(db.choose_design_parameters.product_in_quotation_id == product.id).select()
                for i in parameter_table:
                    i.delete_record()
                profile_table = db(db.choose_profile.product_in_quotation_id == product.id).select()
                for i in profile_table:
                    i.delete_record()
                reinforcement_table = db(db.choose_reinforcement.product_in_quotation_id == product.id).select()
                for i in reinforcement_table:
                    i.delete_record()
                HAA_table = db(db.choose_hardware.product_in_quotation_id == product.id).select()
                for i in HAA_table:
                    i.delete_record()
                glass_table = db(db.choose_glass.product_in_quotation_id == product.id).select()
                for i in glass_table:
                    i.delete_record()
                material_table = db(db.choose_material.product_in_quotation_id == product.id).select()
                for i in material_table:
                    i.delete_record()
                extra_info_table = db(db.choose_extra.product_in_quotation_id == product.id).select()
                for i in extra_info_table:
                    i.delete_record()

                product.delete_record()
            entry.delete_record()

        #Deleting Products and associated entries
        product_list = db(db.product.project_id == project.id).select()
        for entry in product_list:

            design_parameters_values_list = db(db.design_parameters_values.product_id == entry.id).select()
            for parameter in design_parameters_values_list:
                parameter.delete_record()

            profile_values_list = db(db.profile_values.product_id == entry.id).select()
            for profile in profile_values_list:
                profile.delete_record()

            reinforcement_values_list = db(db.reinforcement_values.product_id == entry.id).select()
            for reinforcement in reinforcement_values_list:
                reinforcement.delete_record()

            hardware_and_accessories_values_list = db(db.hardware_and_accessories_values.product_id == entry.id).select()
            for hardware in hardware_and_accessories_values_list:
                hardware.delete_record()

            glass_values_list = db(db.glass_values.product_id == entry.id).select()
            for glass in glass_values_list:
                glass.delete_record()

            installation_material_values_list = db(db.installation_material_values.product_id == entry.id).select()
            for material in installation_material_values_list:
                material.delete_record()

            extra_information_values_list = db(db.extra_information_values.product_id == entry.id).select()
            for info in extra_information_values_list:
                info.delete_record()

            product_cost_list = db(db.product_cost.product_id == entry.id).select()
            for cost in product_cost_list:
                cost.delete_record()
            entry.delete_record()
        project.delete_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed project entry Name: ' + project.name + ' Address: ' + project.address + ' Description: ' + project.description + ' Phase: ' + project.phase + 'Registered Date: ' + project.registered_date.strftime('%d-%m-%Y'), log_time = datetime.datetime.now())
    redirect('index.html')
    response.flash = 'Success'
    return dict()

#endregion

#region Organization and Point of Contact
#---------------------------------------- ADD/UPDATE/DELETE ORGANIZATION AND POC DETAILS ---------------------------------------------#
@auth.requires_login()
def add_new_organization():
    form = SQLFORM(db.organization)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted organization entry ' + form.vars.name, log_time = datetime.datetime.now())
        redirect(URL('index.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form = form)

@auth.requires_login()
def update_organization():
    org_id = request.vars.entry_id
    l = db(db.organization.id == org_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_address = i.address
        form = SQLFORM(db.organization, i, showid=False, deletable=False)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated organization entry Name: ' + old_name + ' Address: ' + old_address + ' to Name: ' + form.vars.name + ' Address: ' + form.vars.address, log_time = datetime.datetime.now())
            redirect(URL('index.html'))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please update'
    return dict(form=form)

@auth.requires_login()
def add_new_POC():
    form = SQLFORM(db.point_of_contact)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted point of contact ' + form.vars.name, log_time = datetime.datetime.now())
        redirect(URL('index.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form = form)

@auth.requires_login()
def update_POC():
    POC_id = request.vars.entry_id
    l = db(db.point_of_contact.id == POC_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_number = i.phone_number
        old_email = i.email
        old_designation = i.designation
        form = SQLFORM(db.point_of_contact, i, showid=False, deletable=False)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated point of contact Name: ' + old_name + ' Phone Number: ' + old_number + ' Email: ' + old_email + ' Designation: ' + old_designation +
                                       ' to Name: ' + form.vars.name + + ' Phone Number: ' + form.vars.phone_number + ' Email: ' + form.vars.email + ' Designation: ' + form.vars.designation, log_time = datetime.datetime.now())
            redirect(URL('index.html'))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please update'
    return dict(form=form)

@auth.requires_login()
def delete_POC():
    POC_list = db(db.point_of_contact.id >= 0).select()
    return dict(POC_list = POC_list)
@auth.requires_login()
def delete_POC_helper():
    POC_list = []
    for var in request.vars:
        try:
            POC_list.append(int(var))
        except:
            pass
    delete_list = db((db.point_of_contact.id >= 0) & (db.point_of_contact.id.belongs(POC_list))).select()
    for user in delete_list:
        project_to_user_list = db(db.project_to_poc.poc_id == user.id).select()
        for entry in project_to_user_list:
            entry.delete_record()
        user.delete_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed point of contact ' + user.name + ' ' + user.phone_number, log_time = datetime.datetime.now())
    redirect('index.html')
    response.flash = 'Success'
    return dict()

#endregion

#endregion

#region Document Generation
#################################################################################################################
#------------------------------------------- DOCUMENT GENERATION -----------------------------------------------#
#################################################################################################################

@auth.requires_login()
def generate_document():
    doc = request.vars.document_type
    project_id = request.vars.project_id
    if doc == 'profile_cutting_list':
        redirect(URL('generate_profile_cutting_list',vars=dict(project_id = project_id)))
    elif doc == 'glass_cutting_list':
        redirect(URL('generate_glass_cutting_list',vars=dict(project_id = project_id)))
    elif doc == 'accessories_list':
        redirect(URL('generate_accessories_list',vars=dict(project_id = project_id)))
    elif doc == 'installation_material_list':
        redirect(URL('generate_installation_material_list',vars=dict(project_id = project_id)))
    elif doc == 'QC':
        redirect(URL('generate_QC',vars=dict(project_id = project_id)))
    return dict()

@auth.requires_login()
def generate_profile_cutting_list():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    TOP_MARGIN = 5
    FONT_SIZE = 10
    MAIN_BORDER_SIZE = 0.5
    PADDING = MAIN_BORDER_SIZE
    IMAGE_WIDTH = 60
    IMAGE_HEIGHT = 20
    QC_TEXTBOX_WIDTH = 20
    TEXTBOX_BORDER_SIZE = 0.1
    NUM_STICKERS_PER_PAGE = 16
    MIDDLE_BORDER_X = 2
    MIDDLE_BORDER_Y = 10

    CELL_WIDTH = IMAGE_WIDTH + 2*QC_TEXTBOX_WIDTH + MAIN_BORDER_SIZE + PADDING
    CELL_HEIGHT = IMAGE_HEIGHT + MAIN_BORDER_SIZE + PADDING
    TEXTBOX_WIDTH = (CELL_WIDTH - MAIN_BORDER_SIZE)/4
    TEXTBOX_HEIGHT = (CELL_HEIGHT - MAIN_BORDER_SIZE)/3
    TEXTBOX_PROJECT_X = LEFT_MARGIN + MAIN_BORDER_SIZE
    TEXTBOX_PROJECT_Y = TOP_MARGIN + MAIN_BORDER_SIZE
    TEXTBOX_PROFILE_CODE_X = TEXTBOX_PROJECT_X + TEXTBOX_WIDTH
    TEXTBOX_PROFILE_CODE_Y = TEXTBOX_PROJECT_Y + TEXTBOX_HEIGHT
    TEXTBOX_POSITION_X = TEXTBOX_PROFILE_CODE_X + TEXTBOX_WIDTH
    TEXTBOX_POSITION_Y = TEXTBOX_PROFILE_CODE_Y + TEXTBOX_HEIGHT
    TEXTBOX_LOCATION_VALUE_X = TEXTBOX_POSITION_X + TEXTBOX_WIDTH

    project_id = request.vars.project_id
    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()

    products = db(db.product.project_id == project_id).select()
    project = db(db.project.id == project_id).select()[0]
    i = 0
    for k in range(len(products)):
        design = db(db.design.id == products[k].design_id).select()[0]
        profile = db(db.profile_used_in_design.design_id == design.id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
        block_number = products[k].block_number
        flat_number = products[k].flat_number
        window_number = products[k].window_number

        for j in range(len(profile)):

            profile_values = db((db.profile_values.product_id == products[k].id) & (db.profile_values.profile_used_in_design_id == profile[j].profile_used_in_design.id)).select()
            if len(profile_values) > 0:
                if i%NUM_STICKERS_PER_PAGE == 0:
                        pdf.add_page()
                        pdf.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
                        pdf.set_font('Times', '', FONT_SIZE)

                #Position
                POS_X = ((i%NUM_STICKERS_PER_PAGE)%2)*(CELL_WIDTH + MIDDLE_BORDER_X)
                POS_Y = ((i%NUM_STICKERS_PER_PAGE)/2)*(CELL_HEIGHT + MIDDLE_BORDER_Y)

                #Project, Profile, Cut Angle
                pdf.set_xy(LEFT_MARGIN + POS_X,TOP_MARGIN + POS_Y)
                pdf.set_line_width(MAIN_BORDER_SIZE)
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, border=1)
                pdf.set_xy(TEXTBOX_PROJECT_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.set_line_width(TEXTBOX_BORDER_SIZE)
                pdf.set_font('Times', '', FONT_SIZE)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Project', border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROJECT_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Profile', border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROJECT_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Cut Angle', border='R', align='C')

                #Project Code, Profile Code, Angle
                pdf.set_font('Times', 'B', FONT_SIZE)
                pdf.set_xy(TEXTBOX_PROFILE_CODE_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, project.name, border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROFILE_CODE_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, profile[j].profile.profile_code, border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROFILE_CODE_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, profile_values[0].cut, border='R', align='C')

                #Location, Size, Position
                pdf.set_font('Times', '', FONT_SIZE)
                pdf.set_xy(TEXTBOX_POSITION_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Location', border='BR', align='C')
                pdf.set_xy(TEXTBOX_POSITION_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Size', border='BR', align='C')
                pdf.set_xy(TEXTBOX_POSITION_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Position', border='R', align='C')

                #Location Value, Size Value, Position Value
                pdf.set_font('Times', 'B', FONT_SIZE)
                pdf.set_xy(TEXTBOX_LOCATION_VALUE_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, str(block_number)+'/'+str(flat_number)+'/'+str(window_number), border='B', align='C')
                pdf.set_xy(TEXTBOX_LOCATION_VALUE_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, str(profile_values[0].length_value), border='B', align='C')
                pdf.set_xy(TEXTBOX_LOCATION_VALUE_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, profile_values[0].profile_position, align='C')

                i += 1

    response.headers['Content-Type'] = 'application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
def generate_glass_cutting_list():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    TOP_MARGIN = 5
    FONT_SIZE = 10
    MAIN_BORDER_SIZE = 0.5
    PADDING = MAIN_BORDER_SIZE
    IMAGE_WIDTH = 60
    IMAGE_HEIGHT = 20
    QC_TEXTBOX_WIDTH = 20
    TEXTBOX_BORDER_SIZE = 0.1
    NUM_STICKERS_PER_PAGE = 16
    MIDDLE_BORDER_X = 2
    MIDDLE_BORDER_Y = 10

    CELL_WIDTH = IMAGE_WIDTH + 2*QC_TEXTBOX_WIDTH + MAIN_BORDER_SIZE + PADDING
    CELL_HEIGHT = IMAGE_HEIGHT + MAIN_BORDER_SIZE + PADDING
    TEXTBOX_WIDTH = (CELL_WIDTH - MAIN_BORDER_SIZE)/4
    TEXTBOX_HEIGHT = (CELL_HEIGHT - MAIN_BORDER_SIZE)/3
    TEXTBOX_PROJECT_X = LEFT_MARGIN + MAIN_BORDER_SIZE
    TEXTBOX_PROJECT_Y = TOP_MARGIN + MAIN_BORDER_SIZE
    TEXTBOX_PROFILE_CODE_X = TEXTBOX_PROJECT_X + TEXTBOX_WIDTH
    TEXTBOX_PROFILE_CODE_Y = TEXTBOX_PROJECT_Y + TEXTBOX_HEIGHT
    TEXTBOX_POSITION_X = TEXTBOX_PROFILE_CODE_X + TEXTBOX_WIDTH
    TEXTBOX_POSITION_Y = TEXTBOX_PROFILE_CODE_Y + TEXTBOX_HEIGHT
    TEXTBOX_LOCATION_VALUE_X = TEXTBOX_POSITION_X + TEXTBOX_WIDTH

    project_id = request.vars.project_id
    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()

    products = db(db.product.project_id == project_id).select()
    project = db(db.project.id == project_id).select()[0]
    i = 0
    for k in range(len(products)):
        design = db(db.design.id == products[k].design_id).select()[0]
        glass = db(db.glass_used_in_design.design_id == design.id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
        block_number = products[k].block_number
        flat_number = products[k].flat_number
        window_number = products[k].window_number

        for j in range(len(glass)):
            glass_values = db((db.glass_values.product_id == products[k].id) & (db.glass_values.glass_used_in_design_id == glass[j].glass_used_in_design.id)).select()
            if len(glass_values) > 0:
                if i%NUM_STICKERS_PER_PAGE == 0:
                        pdf.add_page()
                        pdf.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
                        pdf.set_font('Times', '', FONT_SIZE)

                #Position
                POS_X = ((i%NUM_STICKERS_PER_PAGE)%2)*(CELL_WIDTH + MIDDLE_BORDER_X)
                POS_Y = ((i%NUM_STICKERS_PER_PAGE)/2)*(CELL_HEIGHT + MIDDLE_BORDER_Y)

                #Project, Profile, Cut Angle
                pdf.set_xy(LEFT_MARGIN + POS_X,TOP_MARGIN + POS_Y)
                pdf.set_line_width(MAIN_BORDER_SIZE)
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, border=1)
                pdf.set_xy(TEXTBOX_PROJECT_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.set_line_width(TEXTBOX_BORDER_SIZE)
                pdf.set_font('Times', '', FONT_SIZE)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Project', border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROJECT_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Glass Type', border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROJECT_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, border='R', align='C')

                #Project Code, Profile Code, Angle
                pdf.set_font('Times', 'B', FONT_SIZE)
                pdf.set_xy(TEXTBOX_PROFILE_CODE_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, project.name, border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROFILE_CODE_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, glass[j].glass.name, border='BR', align='C')
                pdf.set_xy(TEXTBOX_PROFILE_CODE_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, border='R', align='C')

                #Location, Size, Position
                pdf.set_font('Times', '', FONT_SIZE)
                pdf.set_xy(TEXTBOX_POSITION_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Location', border='BR', align='C')
                pdf.set_xy(TEXTBOX_POSITION_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Width', border='BR', align='C')
                pdf.set_xy(TEXTBOX_POSITION_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, 'Height', border='R', align='C')

                #Location Value, Size Value, Position Value
                pdf.set_font('Times', 'B', FONT_SIZE)
                pdf.set_xy(TEXTBOX_LOCATION_VALUE_X + POS_X, TEXTBOX_PROJECT_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, str(block_number)+'/'+str(flat_number)+'/'+str(window_number), border='B', align='C')
                pdf.set_xy(TEXTBOX_LOCATION_VALUE_X + POS_X, TEXTBOX_PROFILE_CODE_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, str(glass_values[0].width), border='B', align='C')
                pdf.set_xy(TEXTBOX_LOCATION_VALUE_X + POS_X, TEXTBOX_POSITION_Y + POS_Y)
                pdf.cell(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, str(glass_values[0].height), align='C')

                i += 1

    response.headers['Content-Type'] = 'application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
def generate_accessories_list():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    TOP_MARGIN = 5
    FONT_SIZE = 12
    TITLE_FONT_SIZE = 15
    CELL_WIDTH = 190
    CELL_HEIGHT = 12
    TABLE_START_X = 25
    TABLE_START_Y = 50
    SNO_WIDTH = 10
    SNO_HEIGHT = 5
    ITEM_CODE_WIDTH = 30
    ITEM_DESC_WIDTH = 100
    QUANTITY_WIDTH =  20
    ITEM_CODE_X = TABLE_START_X + SNO_WIDTH
    ITEM_DESC_X = ITEM_CODE_X + ITEM_CODE_WIDTH
    QUANTITY_X = ITEM_DESC_X + ITEM_DESC_WIDTH
    NUM_ENTRIES_PER_PAGE = 40

    project_id = request.vars.project_id
    class PDF(FPDF):
        def header(self):
            self.set_font('Times', 'B', TITLE_FONT_SIZE)
            self.cell(w = 0, txt = 'PRIME uPVC DOORS AND WINDOWS', align = 'C')
            self.ln(7)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(w = 0, txt = 'Production Document', ln = 0, align = 'L')
            self.cell(w = 0, txt = str(datetime.date.today().strftime('Date : %d-%m-%Y')), align = 'R')
            self.ln(5)

        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()

    products = db(db.product.project_id == project_id).select()
    project = db(db.project.id == project_id).select()[0]
    i = 0
    for k in range(len(products)):
        design = db(db.design.id == products[k].design_id).select()[0]
        hardware = db(db.hardware_and_accessories_used_in_design.design_id == design.id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))

        for j in range(len(hardware)):
            HAA_values = db((db.hardware_and_accessories_values.product_id == products[k].id) & (db.hardware_and_accessories_values.hardware_and_accessories_used_in_design_id == hardware[j].hardware_and_accessories_used_in_design.id)).select()
            if len(HAA_values) > 0:
                if i%NUM_ENTRIES_PER_PAGE == 0:
                    pdf.add_page()
                    pdf.set_font('Times', '', FONT_SIZE)

                    #Heading box
                    pdf.cell(CELL_WIDTH, CELL_HEIGHT, txt='', border=1)
                    #pdf.set_xy(10, 25)
                    #pdf.cell(w=0, txt='Production Doc No :    24', ln=0, align='L')
                    pdf.set_xy(120, 25)
                    pdf.cell(w=0, txt='Project Name :    ' + project.name, ln=1, align='L')
                    pdf.set_xy(120, 30)
                    pdf.cell(w=0, txt='Document Type:    Accessories', ln=1, align='L')
                    pdf.ln(10)

                    #Table Header
                    pdf.set_xy(TABLE_START_X, TABLE_START_Y)
                    pdf.cell(w=SNO_WIDTH, h=SNO_HEIGHT, txt='S.No', border=1, align='C')
                    pdf.set_xy(ITEM_CODE_X, TABLE_START_Y)
                    pdf.cell(w=ITEM_CODE_WIDTH, h=SNO_HEIGHT, txt='Item Code', border='RTB', align='C')
                    pdf.set_xy(ITEM_DESC_X, TABLE_START_Y)
                    pdf.cell(w=ITEM_DESC_WIDTH, h=SNO_HEIGHT, txt='Item Description', border='RTB', align='C')
                    pdf.set_xy(QUANTITY_X, TABLE_START_Y)
                    pdf.cell(w=QUANTITY_WIDTH, h=SNO_HEIGHT, txt='Quantity', border='RTB', align='C')

                #Table
                POS_Y = ((i%NUM_ENTRIES_PER_PAGE)+1)*SNO_HEIGHT

                pdf.set_xy(TABLE_START_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=SNO_WIDTH, h=SNO_HEIGHT, txt=str(i+1), border=1, align='C')
                pdf.set_xy(ITEM_CODE_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=ITEM_CODE_WIDTH, h=SNO_HEIGHT, txt=hardware[j].hardware_and_accessories.name, border='RTB', align='C')
                pdf.set_xy(ITEM_DESC_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=ITEM_DESC_WIDTH, h=SNO_HEIGHT, txt=hardware[j].hardware_and_accessories.description, border='RTB', align='C')
                pdf.set_xy(QUANTITY_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=QUANTITY_WIDTH, h=SNO_HEIGHT, txt=str(HAA_values[0].quantity), border='RTB', align='C')

                i += 1

    response.headers['Content-Type'] = 'application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
def generate_installation_material_list():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    TOP_MARGIN = 5
    FONT_SIZE = 12
    TITLE_FONT_SIZE = 15
    CELL_WIDTH = 190
    CELL_HEIGHT = 12
    TABLE_START_X = 25
    TABLE_START_Y = 50
    SNO_WIDTH = 10
    SNO_HEIGHT = 5
    ITEM_CODE_WIDTH = 30
    ITEM_DESC_WIDTH = 100
    QUANTITY_WIDTH =  20
    ITEM_CODE_X = TABLE_START_X + SNO_WIDTH
    ITEM_DESC_X = ITEM_CODE_X + ITEM_CODE_WIDTH
    QUANTITY_X = ITEM_DESC_X + ITEM_DESC_WIDTH
    NUM_ENTRIES_PER_PAGE = 40

    project_id = request.vars.project_id
    class PDF(FPDF):
        def header(self):
            self.set_font('Times', 'B', TITLE_FONT_SIZE)
            self.cell(w = 0, txt = 'PRIME uPVC DOORS AND WINDOWS', align = 'C')
            self.ln(7)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(w = 0, txt = 'Production Document', ln = 0, align = 'L')
            self.cell(w = 0, txt = str(datetime.date.today().strftime('Date : %d-%m-%Y')), align = 'R')
            self.ln(5)

        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()

    products = db(db.product.project_id == project_id).select()
    project = db(db.project.id == project_id).select()[0]
    i = 0
    for k in range(len(products)):
        design = db(db.design.id == products[k].design_id).select()[0]
        material = db(db.installation_material_used_in_design.design_id == design.id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))

        for j in range(len(material)):
            material_values = db((db.installation_material_values.product_id == products[k].id) & (db.installation_material_values.installation_material_used_in_design_id == material[j].installation_material_used_in_design.id)).select()
            if len(material_values) > 0:
                if i%NUM_ENTRIES_PER_PAGE == 0:
                    pdf.add_page()
                    pdf.set_font('Times', '', FONT_SIZE)

                    #Heading box
                    pdf.cell(CELL_WIDTH, CELL_HEIGHT, txt='', border=1)
                    #pdf.set_xy(10, 25)
                    #pdf.cell(w=0, txt='Production Doc No :    24', ln=0, align='L')
                    pdf.set_xy(120, 25)
                    pdf.cell(w=0, txt='Project Name :    ' + project.name, ln=1, align='L')
                    pdf.set_xy(120, 30)
                    pdf.cell(w=0, txt='Document Type:    Installation Material', ln=1, align='L')
                    pdf.ln(10)

                    #Table Header
                    pdf.set_xy(TABLE_START_X, TABLE_START_Y)
                    pdf.cell(w=SNO_WIDTH, h=SNO_HEIGHT, txt='S.No', border=1, align='C')
                    pdf.set_xy(ITEM_CODE_X, TABLE_START_Y)
                    pdf.cell(w=ITEM_CODE_WIDTH, h=SNO_HEIGHT, txt='Item Code', border='RTB', align='C')
                    pdf.set_xy(ITEM_DESC_X, TABLE_START_Y)
                    pdf.cell(w=ITEM_DESC_WIDTH, h=SNO_HEIGHT, txt='Item Description', border='RTB', align='C')
                    pdf.set_xy(QUANTITY_X, TABLE_START_Y)
                    pdf.cell(w=QUANTITY_WIDTH, h=SNO_HEIGHT, txt='Quantity', border='RTB', align='C')


                #Table
                POS_Y = ((i%NUM_ENTRIES_PER_PAGE)+1)*SNO_HEIGHT

                pdf.set_xy(TABLE_START_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=SNO_WIDTH, h=SNO_HEIGHT, txt=str(i+1), border=1, align='C')
                pdf.set_xy(ITEM_CODE_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=ITEM_CODE_WIDTH, h=SNO_HEIGHT, txt=material[j].installation_material.name, border='RTB', align='C')
                pdf.set_xy(ITEM_DESC_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=ITEM_DESC_WIDTH, h=SNO_HEIGHT, txt=material[j].installation_material.description, border='RTB', align='C')
                pdf.set_xy(QUANTITY_X, TABLE_START_Y + POS_Y)
                pdf.cell(w=QUANTITY_WIDTH, h=SNO_HEIGHT, txt=str(material_values[0].quantity), border='RTB', align='C')

                i += 1

    response.headers['Content-Type'] = 'application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
def generate_QC():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    TOP_MARGIN = 5
    FONT_SIZE = 12
    QC_FONT_SIZE = 24
    MAIN_BORDER_SIZE = 0.5
    PADDING = MAIN_BORDER_SIZE
    IMAGE_WIDTH = 60
    IMAGE_HEIGHT = 20
    TEXTBOX_WIDTH = 20
    UPPER_TEXTBOX_HEIGHT = 5
    LOWER_TEXTBOX_HEIGHT = IMAGE_HEIGHT - UPPER_TEXTBOX_HEIGHT
    TEXTBOX_BORDER_SIZE = 0.1
    NUM_STICKERS_PER_PAGE = 16
    MIDDLE_BORDER_X = 2
    MIDDLE_BORDER_Y = 10

    CELL_WIDTH = IMAGE_WIDTH + 2*TEXTBOX_WIDTH + MAIN_BORDER_SIZE + PADDING
    CELL_HEIGHT = IMAGE_HEIGHT + MAIN_BORDER_SIZE + PADDING
    IMAGE_X = LEFT_MARGIN + MAIN_BORDER_SIZE
    IMAGE_Y = TOP_MARGIN + MAIN_BORDER_SIZE
    TEXTBOX_LOCATION_X = IMAGE_X + IMAGE_WIDTH
    TEXTBOX_LOCATION_Y = IMAGE_Y
    TEXTBOX_OK_X = TEXTBOX_LOCATION_X + TEXTBOX_WIDTH
    TEXTBOX_OK_Y = IMAGE_Y + UPPER_TEXTBOX_HEIGHT

    project_id = request.vars.project_id
    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()

    products = db(db.product.project_id == project_id).select()
    for i in range(len(products)):
        if i%NUM_STICKERS_PER_PAGE == 0:
            pdf.add_page()
            pdf.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
            pdf.set_font('Times', '', FONT_SIZE)

        block_number = products[i].block_number
        flat_number = products[i].flat_number
        window_number = products[i].window_number

        #Position
        POS_X = ((i%NUM_STICKERS_PER_PAGE)%2)*(CELL_WIDTH + MIDDLE_BORDER_X)
        POS_Y = ((i%NUM_STICKERS_PER_PAGE)/2)*(CELL_HEIGHT + MIDDLE_BORDER_Y)

        #Logo
        pdf.set_xy(LEFT_MARGIN + POS_X,TOP_MARGIN + POS_Y)
        pdf.set_line_width(MAIN_BORDER_SIZE)
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, border=1)
        pdf.set_xy(IMAGE_X + POS_X, IMAGE_Y + POS_Y)
        pdf.image('./applications/Prime/static/images/prime.jpeg', w = IMAGE_WIDTH, h = IMAGE_HEIGHT)

        #Location,QC
        pdf.set_line_width(TEXTBOX_BORDER_SIZE)
        pdf.set_xy(TEXTBOX_LOCATION_X + POS_X, TEXTBOX_LOCATION_Y + POS_Y)
        pdf.set_font('Times', '', FONT_SIZE)
        pdf.cell(TEXTBOX_WIDTH, UPPER_TEXTBOX_HEIGHT, 'Location', border='LR', align='C')
        pdf.set_xy(TEXTBOX_LOCATION_X + POS_X, TEXTBOX_OK_Y + POS_Y)
        pdf.set_font('Times', 'B', QC_FONT_SIZE)
        pdf.cell(TEXTBOX_WIDTH, LOWER_TEXTBOX_HEIGHT, 'QC', border='LRT', align='C')

        #Location Value,OK
        pdf.set_xy(TEXTBOX_OK_X + POS_X, TEXTBOX_LOCATION_Y + POS_Y)
        pdf.set_font('Times', '', FONT_SIZE)
        pdf.cell(TEXTBOX_WIDTH, UPPER_TEXTBOX_HEIGHT, str(block_number)+'/'+str(flat_number)+'/'+str(window_number), align='C')
        pdf.set_xy(TEXTBOX_OK_X + POS_X, TEXTBOX_OK_Y + POS_Y)
        pdf.set_font('Times', 'B', QC_FONT_SIZE)
        pdf.cell(TEXTBOX_WIDTH, LOWER_TEXTBOX_HEIGHT, 'OK', border='T', align='C')

    response.headers['Content-Type'] = 'application/pdf'
    return pdf.output(dest='S')

#region Generate Quotation
#---------------------------------------- GENERATE QUOTATION ---------------------------------------------#
@auth.requires_login()
def quotation_options():
    project_id = request.vars.project_id
    quotations = db((db.documents.project_id == project_id) & (db.documents.document_type == 'Quotation')).select()
    name = 'Quotation_' + str(len(quotations)+1)
    db.documents.insert(project_id = project_id, name = name, document_type = 'Quotation')
    document_id = db(db.documents.name == name).select()[0].id
    return dict(document_id = document_id, quotations = quotations)

@auth.requires_login()
def copy_quotation():
    entry_id = request.vars.entry_id
    document_id = request.vars.document_id
    quotation_product_list = db(db.product_in_quotation.document_id == entry_id).select()
    for product in quotation_product_list:

        new_id = db.product_in_quotation.insert(name = product.name, design_id = product.design_id, document_id = document_id, quantity = product.quantity, profile_cost = product.profile_cost,
                          reinforcement_cost = product.reinforcement_cost, hardware_and_accessories_cost = product.hardware_and_accessories_cost, glass_cost = product.glass_cost, installation_material_cost = product.installation_material_cost,
                          fabrication_cost = product.fabrication_cost, installation_cost = product.installation_cost, total_value = product.total_value, profit_margin_id = product.profit_margin_id,
                          final_value = product.final_value, total_value_per_piece = product.total_value_per_piece)

        #Copying Values
        product_quotation_parameter_values_list = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select()
        for entry in product_quotation_parameter_values_list:
            db.product_quotation_parameter_values.insert(product_in_quotation_id = new_id, design_parameter_id = entry.design_parameter_id, parameter_value = entry.parameter_value)

        product_quotation_glass_values_list = db(db.product_quotation_glass_values.product_in_quotation_id == product.id).select()
        for entry in product_quotation_glass_values_list:
            db.product_quotation_glass_values.insert(product_in_quotation_id = new_id, glass_used_in_design_id = entry.glass_used_in_design_id, width = entry.width, height = entry.height, quantity = entry.quantity, glass_cost = entry.glass_cost)

        product_quotation_hardware_values_list = db(db.product_quotation_hardware_values.product_in_quotation_id == product.id).select()
        for entry in product_quotation_hardware_values_list:
            db.product_quotation_hardware_values.insert(product_in_quotation_id = new_id, hardware_and_accessories_used_in_design_id = entry.hardware_and_accessories_used_in_design_id, quantity = entry.quantity, hardware_and_accessories_cost = entry.hardware_and_accessories_cost)

        product_quotation_extra_information_values_list = db(db.product_quotation_extra_information_values.product_in_quotation_id == product.id).select()
        for entry in product_quotation_extra_information_values_list:
            db.product_quotation_extra_information_values.insert(product_in_quotation_id = new_id, extra_information_in_design_id = entry.extra_information_in_design_id, default_value = entry.default_value, extra_information_value = entry.extra_information_value)

        choose_params = db(db.choose_design_parameters.product_in_quotation_id == product.id).select()
        for entry in choose_params:
            db.choose_design_parameters.insert(product_in_quotation_id = new_id, param_id = entry.param_id)
        choose_profile = db(db.choose_profile.product_in_quotation_id == product.id).select()
        for entry in choose_profile:
            db.choose_profile.insert(product_in_quotation_id = new_id, pro_id = entry.pro_id)
        choose_reinforcement = db(db.choose_reinforcement.product_in_quotation_id == product.id).select()
        for entry in choose_reinforcement:
            db.choose_reinforcement.insert(product_in_quotation_id = new_id, rein_id = entry.rein_id)
        choose_hardware = db(db.choose_hardware.product_in_quotation_id == product.id).select()
        for entry in choose_hardware:
            db.choose_hardware.insert(product_in_quotation_id = new_id, hardware_id = entry.hardware_id)
        choose_glass = db(db.choose_glass.product_in_quotation_id == product.id).select()
        for entry in choose_glass:
            db.choose_glass.insert(product_in_quotation_id = new_id, glas_id = entry.glas_id)
        choose_material = db(db.choose_material.product_in_quotation_id == product.id).select()
        for entry in choose_material:
            db.choose_material.insert(product_in_quotation_id = new_id, material_id = entry.material_id)
        choose_extra = db(db.choose_extra.product_in_quotation_id == product.id).select()
        for entry in choose_extra:
            db.choose_extra.insert(product_in_quotation_id = new_id, extra_info_id = entry.extra_info_id)

    redirect(URL('generate_quotation_details.html',vars = dict(document_id = document_id)))

@auth.requires_login()
def generate_quotation_details():
    document_id = request.vars.document_id
    document = db(db.documents.id == document_id).select()[0]
    project = db(db.project.id == document.project_id).select()
    project_id = project[0].id
    product_list = db(db.product_in_quotation.document_id == document_id).select()
    org = None
    for i in project:
        org = db(db.organization.id == i.organization_id).select()
    return dict(project = project, org = org, project_id = project_id, document_id = document_id, product_list = product_list)

@auth.requires_login()
def add_new_product_quotation():
    document_id=request.vars.document_id
    rows=db(db.product_in_quotation.document_id == document_id).select(db.product_in_quotation.name)
    max=0
    for i in rows:
        try:
            number=int(re.search(r'\d+', i.name).group())
            if(number>max):
                max=number
        except:
            pass
    db.product_in_quotation.document_id.default = document_id
    db.product_in_quotation.name.default = 'product_' + str(max+1)
    form=SQLFORM(db.product_in_quotation,fields=['design_id', 'quantity', 'fabrication_cost', 'installation_cost', 'profit_margin_id'])
    if form.process().accepted:
        session.flash = 'accepted'
        id=form.vars.id
        redirect(URL('product_in_quotation_design_parameters.html', vars=dict(product_id=id)))
    elif form.errors:
           response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def product_in_quotation_design_parameters():
    product_id = request.vars.product_id
    product = db(db.product_in_quotation.id == product_id).select()
    sel = []
    for i in product:
        sel=db(db.design_parameters.design_id == i.design_id).select()
    parameters={}
    parameters=collections.OrderedDict(sorted(parameters.items()))
    for row in sel:
        parameters[row.id]=row.name+'('+row.codename+')'
    return dict(parameters = parameters, product_id = product_id)

@auth.requires_login()
def quotation_design_parameters_values():
    product_id=request.vars.product_id
    product = db(db.product_in_quotation.id == product_id).select()[0]
    document = db(db.documents.id == product.document_id).select()[0]
    project = db(db.project.id == document.project_id).select()[0]
    parameters=request.vars
    del parameters['product_id']
    parameter_value=[]
    for parameter in parameters:
        db.product_quotation_parameter_values.insert(product_in_quotation_id=product_id,design_parameter_id=parameter,parameter_value=parameters[parameter])
        parameter_value.append(parameters[parameter])
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' added product ' + product.name + ' in quotation ' + document.name + ' of project ' + project.name, log_time = datetime.datetime.now())
    redirect(URL('calculate_quotation_product',vars=dict(entry_id = product_id)))
    return dict()

@auth.requires_login()
def calculate_quotation_product():
    product_id = request.vars.entry_id
    flag = request.vars.flag
    product = db(db.product_in_quotation.id == product_id).select()[0]
    design_id = product.design_id
    design_table = db(db.design.id == design_id).select()[0]
    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product_id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
    parameter_value = []
    for i in parameter_values_table:
        parameter_value.append(str(i.parameter_value))
    profit_margin_table = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]

    profile_cost = 0.0
    reinforcement_cost = 0.0
    hardware_cost = 0.0
    glass_cost = 0.0
    material_cost = 0.0

    if flag:
        rows = db(db.product_quotation_hardware_values.product_in_quotation_id == product_id).delete()
        rows = db(db.product_quotation_glass_values.product_in_quotation_id == product_id).delete()
        rows = db(db.product_quotation_extra_information_values.product_in_quotation_id == product_id).delete()

    parameter_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product_id).select(join = db.product_quotation_parameter_values.on(db.design_parameters.id == db.product_quotation_parameter_values.design_parameter_id))
    for i in parameter_table:
        if i.design_parameters.name.lower() == 'width' or i.design_parameters.name.lower() == 'height':
            db.choose_design_parameters.insert(product_in_quotation_id = product_id, param_id = i.design_parameters.id)

    profile_table = db(db.profile_used_in_design.design_id == design_id).select()
    for i in xrange(len(profile_table)):
        #print profile_table[i].length_calculation,parameter_value
        length_value = Infix(convert(profile_table[i].length_calculation,parameter_value))
        profile_table[i].length_calculation=convert(profile_table[i].length_calculation,parameter_value)
        profile_table[i].length_calculation=Infix(profile_table[i].length_calculation)
        profile_table[i].cost_calculation=convert(profile_table[i].cost_calculation,parameter_value)
        profile_table[i].cost_calculation=Infix(profile_table[i].cost_calculation)
        profile_cost += float(profile_table[i].cost_calculation)

        db.choose_profile.insert(product_in_quotation_id = product_id, pro_id = profile_table[i].profile_id)

    reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select()
    for i in xrange(len(reinforcement_table)):
        #print reinforcement_table[i].length_calculation,parameter_value
        reinforcement_table[i].length_calculation=convert(reinforcement_table[i].length_calculation,parameter_value)
        reinforcement_table[i].length_calculation=Infix(reinforcement_table[i].length_calculation)
        reinforcement_table[i].cost_calculation=convert(reinforcement_table[i].cost_calculation,parameter_value)
        reinforcement_table[i].cost_calculation=Infix(reinforcement_table[i].cost_calculation)
        reinforcement_cost += float(reinforcement_table[i].cost_calculation)

    material_table = db(db.installation_material_used_in_design.design_id == design_id).select()
    for i in xrange(len(material_table)):
        #print material_table[i].cost_calculation,parameter_value
        material_table[i].cost_calculation=convert(material_table[i].cost_calculation,parameter_value)
        material_table[i].cost_calculation=Infix(material_table[i].cost_calculation)
        material_cost += float(material_table[i].cost_calculation)

    HAA_table = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select()
    for i in xrange(len(HAA_table)):
        #print HAA_table[i].cost_calculation,parameter_value
        cost_value = Infix(convert(HAA_table[i].cost_calculation,parameter_value))
        db.product_quotation_hardware_values.insert(product_in_quotation_id = product_id, hardware_and_accessories_used_in_design_id = HAA_table[i].id, quantity = HAA_table[i].quantity, hardware_and_accessories_cost = cost_value)
        hardware_cost += float(cost_value)

        db.choose_hardware.insert(product_in_quotation_id = product_id, hardware_id = HAA_table[i].hardware_and_accessories_id)

    glass_table = db(db.glass_used_in_design.design_id == design_id).select()
    for i in xrange(len(glass_table)):
        #print glass_table[i].width_calculation,parameter_value
        width_value = Infix(convert(glass_table[i].width_calculation,parameter_value))
        height_value = Infix(convert(glass_table[i].height_calculation,parameter_value))
        cost_value = Infix(convert(glass_table[i].cost_calculation,parameter_value))
        db.product_quotation_glass_values.insert(product_in_quotation_id = product_id, glass_used_in_design_id = glass_table[i].id, width = width_value, height = height_value, quantity = glass_table[i].quantity, glass_cost = cost_value)
        glass_cost += float(cost_value)

    extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()
    for i in xrange(len(extra_information_table)):
        value = None
        if extra_information_table[i].calculation:
            #print extra_information_table[i].calculation,parameter_value
            value = Infix(convert(extra_information_table[i].calculation,parameter_value))
        db.product_quotation_extra_information_values.insert(product_in_quotation_id = product_id, extra_information_in_design_id = extra_information_table[i].id, default_value = extra_information_table[i].default_value, extra_information_value = value)

    product.profile_cost = profile_cost
    product.reinforcement_cost = reinforcement_cost
    product.hardware_and_accessories_cost = hardware_cost
    product.glass_cost = glass_cost
    product.installation_material_cost = material_cost
    product.total_value = product.profile_cost + product.reinforcement_cost + product.hardware_and_accessories_cost + product.glass_cost + product.installation_material_cost + product.fabrication_cost + product.installation_cost
    product.total_value = product.total_value*product.quantity
    product.final_value = product.total_value + product.total_value*(profit_margin_table.percentage/100)
    product.total_value_per_piece = product.final_value/product.quantity
    product.update_record()

    redirect(URL('view_quotation_product.html',vars=dict(entry_id = product_id)))
    return dict()

@auth.requires_login()
def view_quotation_product():
    product_id = request.vars.entry_id
    product_table = db(db.product_in_quotation.id == product_id).select()
    product = product_table[0]
    design_id = product.design_id
    document_id = product.document_id
    design_table = db(db.design.id == design_id).select()
    document = db(db.documents.id == document_id).select()[0]
    project_id = document.project_id
    parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product_id).select(orderby=db.design_parameters.id)


    profit_table = db(db.profit_margin_table.id >= 0).select()
    profit_name = db(db.profit_margin_table.id == product.profit_margin_id).select()[0]
    profit_id = profit_name.id
    profit_percentage = profit_name.percentage
    profit_name = profit_name.name
    parameter_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product_id).select(join = db.product_quotation_parameter_values.on(db.design_parameters.id == db.product_quotation_parameter_values.design_parameter_id),orderby=db.design_parameters.id)
    parameter_value = []
    for i in parameter_table:
        parameter_value.append(str(i.product_quotation_parameter_values.parameter_value))

    HAA_values = db((db.product_quotation_hardware_values.product_in_quotation_id == product_id) & (db.product_quotation_hardware_values.hardware_and_accessories_used_in_design_id == db.hardware_and_accessories_used_in_design.id) & (db.hardware_and_accessories_used_in_design.hardware_and_accessories_id == db.hardware_and_accessories.id)).select()
    glass_values = db((db.product_quotation_glass_values.product_in_quotation_id == product_id) & (db.product_quotation_glass_values.glass_used_in_design_id == db.glass_used_in_design.id) & (db.glass_used_in_design.glass_id == db.glass.id)).select()
    extra_values = db((db.product_quotation_extra_information_values.product_in_quotation_id == product_id) & (db.product_quotation_extra_information_values.extra_information_in_design_id == db.extra_information_in_design.id)).select()

    # HAA_values = db(db.product_quotation_hardware_values.product_in_quotation_id == product_id).select()
    # glass_values = db(db.product_quotation_glass_values.product_in_quotation_id == product_id).select()
    # extra_values = db(db.product_quotation_extra_information_values.product_in_quotation_id == product_id).select()

    #profile_table = db(db.profile_used_in_design.design_id == design_id).select()
    profile_table = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
    for i in xrange(len(profile_table)):
        #print profile_table[i].length_calculation,parameter_value
        #length_value = Infix(convert(profile_table[i].lprofile_used_in_design.ength_calculation,parameter_value))
        profile_table[i].profile_used_in_design.length_calculation=convert(profile_table[i].profile_used_in_design.length_calculation,parameter_value)
        profile_table[i].profile_used_in_design.length_calculation=Infix(profile_table[i].profile_used_in_design.length_calculation)
        profile_table[i].profile_used_in_design.cost_calculation=convert(profile_table[i].profile_used_in_design.cost_calculation,parameter_value)
        profile_table[i].profile_used_in_design.cost_calculation=Infix(profile_table[i].profile_used_in_design.cost_calculation)

    #reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select()
    reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
    for i in xrange(len(reinforcement_table)):
        #print reinforcement_table[i].length_calculation,parameter_value
        reinforcement_table[i].reinforcement_used_in_design.length_calculation=convert(reinforcement_table[i].reinforcement_used_in_design.length_calculation,parameter_value)
        reinforcement_table[i].reinforcement_used_in_design.length_calculation=Infix(reinforcement_table[i].reinforcement_used_in_design.length_calculation)
        reinforcement_table[i].reinforcement_used_in_design.cost_calculation=convert(reinforcement_table[i].reinforcement_used_in_design.cost_calculation,parameter_value)
        reinforcement_table[i].reinforcement_used_in_design.cost_calculation=Infix(reinforcement_table[i].reinforcement_used_in_design.cost_calculation)

    #material_table = db(db.installation_material_used_in_design.design_id == design_id).select()
    material_table = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
    for i in xrange(len(material_table)):
        #print material_table[i].cost_calculation,parameter_value
        material_table[i].installation_material_used_in_design.cost_calculation=convert(material_table[i].installation_material_used_in_design.cost_calculation,parameter_value)
        material_table[i].installation_material_used_in_design.cost_calculation=Infix(material_table[i].installation_material_used_in_design.cost_calculation)

    profile_names = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
    reinforcement_names = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
    HAA_names = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))
    glass_names = db(db.glass_used_in_design.design_id == design_id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
    material_names = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
    extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()

    return dict(product_id = product_id, project_id = project_id, document = document, profit_table = profit_table, profit_percentage = profit_percentage, profit_name = profit_name, profit_id = profit_id, parameter_table = parameter_table, product_table = product_table, design_id = design_id, design_table = design_table, profile_table = profile_table, profile_names = profile_names, reinforcement_table = reinforcement_table, reinforcement_names = reinforcement_names, HAA_table = HAA_values, HAA_names = HAA_names, glass_table = glass_values, glass_names = glass_names, material_table = material_table, material_names = material_names, extra_information_table = extra_information_table, extra_values = extra_values)

@auth.requires_login()
def update_product_quotation():
    variables=request.vars
    product_id = variables.product_id
    product_table = db(db.product_in_quotation.id == product_id).select()
    product = db(db.product_in_quotation.id == product_id).select()[0]
    design_id = product.design_id
    document_id = product.document_id
    document = db(db.documents.id == document_id).select()[0]
    project_id = document.project_id
    project = db(db.project.id == project_id).select()[0]

    #profile_values = db(db.profile_values.product_id == product_id).select()
    #reinforcement_values = db(db.reinforcement_values.product_id == product_id).select()
    HAA_values = db(db.product_quotation_hardware_values.product_in_quotation_id == product_id).select()
    glass_values = db(db.product_quotation_glass_values.product_in_quotation_id == product_id).select()
    #material_values = db(db.installation_material_values.product_id == product_id).select()
    extra_values = db(db.product_quotation_extra_information_values.product_in_quotation_id == product_id).select(join = db.product_quotation_extra_information_values.on(db.extra_information_in_design.id == db.product_quotation_extra_information_values.extra_information_in_design_id))
    #extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()

    i=0
    flag=0
    for row in product_table:
        profit_margin_table = db(db.profit_margin_table.id == row.profit_margin_id).select()[0]

        name="name_"+str(i)
        row.name=variables[name]
        name="quantity_"+str(i)
        row.quantity=variables[name]

        name="profile_cost_"+str(i)
        row.profile_cost=variables[name]
        name="reinforcement_cost_"+str(i)
        row.reinforcement_cost=variables[name]
        name="hardware_and_accessories_cost_"+str(i)
        row.hardware_and_accessories_cost=variables[name]
        name="product_glass_cost_"+str(i)
        row.glass_cost=variables[name]
        name="installation_material_cost_"+str(i)
        row.installation_material_cost=variables[name]
        name="fabrication_cost_"+str(i)
        row.fabrication_cost=variables[name]
        name="installation_cost_"+str(i)
        row.installation_cost=variables[name]

        row.total_value = float(row.profile_cost) + float(row.reinforcement_cost) + float(row.hardware_and_accessories_cost) + float(row.glass_cost) + float(row.installation_material_cost) + float(row.fabrication_cost) + float(row.installation_cost)
        row.total_value = row.total_value*int(row.quantity)
        row.final_value = row.total_value + row.total_value*(profit_margin_table.percentage/100)
        row.total_value_per_piece = row.final_value/float(row.quantity)

        row.update_record()
        i=i+1

    """i=0
    for row in profile_values:
        name="profile_position_"+str(i)
        row.profile_position=variables[name]

        name="profile_cut_"+str(i)
        row.cut=variables[name]

        name="profile_quantity_"+str(i)
        row.length_value=variables[name]

        name="profile_length_"+str(i)
        row.quantity=variables[name]

        name="profile_cost_"+str(i)
        row.profile_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in reinforcement_values:
        name="reinforcement_length_"+str(i)
        row.length_value=variables[name]

        name="reinforcement_quantity_"+str(i)
        row.quantity=variables[name]

        name="reinforcement_cost_"+str(i)
        row.reinforcment_cost=variables[name]

        row.update_record()
        i=i+1"""

    i=0
    for row in HAA_values:
        name="HAA_quantity_"+str(i)
        row.quantity=variables[name]

        name="HAA_cost_"+str(i)
        row.hardware_and_accessories_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in glass_values:
        name="glass_width_"+str(i)
        row.width=variables[name]

        name="glass_height_"+str(i)
        row.height=variables[name]

        name="glass_quantity_"+str(i)
        row.quantity=variables[name]

        name="glass_cost_"+str(i)
        row.glass_cost=variables[name]

        row.update_record()
        i=i+1

    """i=0
    for row in material_values:
        name="material_quantity_"+str(i)
        row.quantity=variables[name]

        name="material_cost_"+str(i)
        row.installation_material_cost=variables[name]

        row.update_record()
        i=i+1"""

    i=0
    for row in extra_values:
        if row.extra_information_in_design.default_value:
            name="extra_information_calculation_"+str(i)
            row.product_quotation_extra_information_values.default_value=variables[name]
        elif row.extra_information_in_design.calculation:
            name="extra_information_calculation_"+str(i)
            row.product_quotation_extra_information_values.extra_information_value=variables[name]

        row.product_quotation_extra_information_values.update_record()
        i=i+1

    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated product' + product.name + ' in quotation ' + document.name + ' of project ' + project.name, log_time = datetime.datetime.now())
    redirect(URL('view_quotation_product.html',vars=dict(entry_id = product_id)))

@auth.requires_login()
def update_parameters_quotation():
    product_id = request.vars.product_id
    product = db(db.product_in_quotation.id == product_id).select()
    sel = []
    for i in product:
        sel=db(db.design_parameters.design_id == i.design_id).select(orderby=db.design_parameters.id)
    parameters={}
    parameters=collections.OrderedDict(sorted(parameters.items()))
    for row in sel:
        parameters[row.id]=row.name+'('+row.codename+')'
    return dict(parameters = parameters, product_id = product_id)
@auth.requires_login()
def update_parameters_quotation_helper():
    product_id=request.vars.product_id
    product_parameters = db(db.product_quotation_parameter_values.product_in_quotation_id==product_id).select(orderby=db.product_quotation_parameter_values.design_parameter_id)
    product = db(db.product_in_quotation.id == product_id).select()[0]
    document = db(db.documents.id == product.document_id).select()[0]
    project = db(db.project.id == document.project_id).select()[0]
    parameters=request.vars
    del parameters['product_id']
    for param in product_parameters:
        param.delete_record()
    for parameter in parameters:
        db.product_quotation_parameter_values.insert(product_in_quotation_id=product_id,design_parameter_id=parameter,parameter_value=parameters[parameter])
    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' Updated product' + product.name + ' in document ' + document.name + ' of project ' + project.name, log_time = datetime.datetime.now())
    redirect(URL('calculate_quotation_product',vars=dict(entry_id = product_id, flag = 1)))
    return dict()

@auth.requires_login()
def change_profit():
    product_id = request.vars.product_id
    product=db(db.product_in_quotation.id==product_id).select()[0]
    form=[]
    old_name = db(db.profit_margin_table.id == product.profit_margin_id).select()[0].name
    form = SQLFORM(db.product_in_quotation, product_id, fields=['profit_margin_id'],showid = False)
    if form.process().accepted:
        response.flash = 'form accepted'
        percentage = db(db.profit_margin_table.id == form.vars.profit_margin_id).select()[0]
        product.final_value = product.total_value + product.total_value*(percentage.percentage/100)
        product.total_value_per_piece = product.final_value/float(product.quantity)
        product.profit_margin_id = form.vars.profit_margin_id
        product.update_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated profit margin entry of product ' + product.name + ' from ' + old_name + ' to ' + percentage.name, log_time = datetime.datetime.now())
        redirect(URL('view_quotation_product.html',vars = dict(entry_id = product_id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please update'
    return dict(form=form)

@auth.requires_login()
def delete_quotation_product_helper():
    document_id = request.vars.document_id
    document = db(db.documents.id == document_id).select()[0]
    project = db(db.project.id == document.project_id).select()[0]
    product_list = []
    for var in request.vars:
        try:
            product_list.append(int(var))
        except:
            pass
    delete_list = db((db.product_in_quotation.id >= 0) & (db.product_in_quotation.id.belongs(product_list))).select()
    for product in delete_list:
        #Deleting Products and associated entries
        design_parameters_values_list = db(db.product_quotation_parameter_values.product_in_quotation_id == product.id).select()
        for parameter in design_parameters_values_list:
            parameter.delete_record()

        hardware_and_accessories_values_list = db(db.product_quotation_hardware_values.product_in_quotation_id == product.id).select()
        for hardware in hardware_and_accessories_values_list:
            hardware.delete_record()

        glass_values_list = db(db.product_quotation_glass_values.product_in_quotation_id == product.id).select()
        for glass in glass_values_list:
            glass.delete_record()

        extra_information_values_list = db(db.product_quotation_extra_information_values.product_in_quotation_id == product.id).select()
        for info in extra_information_values_list:
            info.delete_record()

        parameter_table = db(db.choose_design_parameters.product_in_quotation_id == product.id).select()
        for i in parameter_table:
            i.delete_record()
        profile_table = db(db.choose_profile.product_in_quotation_id == product.id).select()
        for i in profile_table:
            i.delete_record()
        reinforcement_table = db(db.choose_reinforcement.product_in_quotation_id == product.id).select()
        for i in reinforcement_table:
            i.delete_record()
        HAA_table = db(db.choose_hardware.product_in_quotation_id == product.id).select()
        for i in HAA_table:
            i.delete_record()
        glass_table = db(db.choose_glass.product_in_quotation_id == product.id).select()
        for i in glass_table:
            i.delete_record()
        material_table = db(db.choose_material.product_in_quotation_id == product.id).select()
        for i in material_table:
            i.delete_record()
        extra_info_table = db(db.choose_extra.product_in_quotation_id == product.id).select()
        for i in extra_info_table:
            i.delete_record()

        product.delete_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed product entry ' + product.name + ' in quotation ' + document.name + ' of project ' + project.name, log_time = datetime.datetime.now())
    redirect(URL('generate_quotation_details.html', vars = dict(document_id = document_id)))
    response.flash = 'Success'
    return dict()

@auth.requires_login()
def generate_quotation_parameters():
    product_id = request.vars.product_id
    product = db(db.product_in_quotation.id == product_id).select()[0]
    document_id = product.document_id
    document = db(db.documents.id == document_id).select()[0]
    project_id = document.project_id
    design_id = product.design_id
    parameter_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product_id).select(join = db.product_quotation_parameter_values.on(db.design_parameters.id == db.product_quotation_parameter_values.design_parameter_id))
    temp = {}
    for i in parameter_table:
        try:
            temp[i.design_parameters.id]
        except:
            temp[i.design_parameters.id] = i
    parameter_table = temp.values()
    """parameter_values_table = db(db.product_quotation_parameter_values.product_in_quotation_id == product_id).select()
    parameter_value = []
    for i in parameter_values_table:
        parameter_value.append(str(i.parameter_value))"""

    choose_params = db(db.choose_design_parameters.product_in_quotation_id == product_id).select(db.choose_design_parameters.param_id)
    choose_params = [d['param_id'] for d in choose_params.as_list()]
    choose_profile = db(db.choose_profile.product_in_quotation_id == product_id).select(db.choose_profile.pro_id)
    choose_profile = [d['pro_id'] for d in choose_profile.as_list()]
    choose_reinforcement = db(db.choose_reinforcement.product_in_quotation_id == product_id).select(db.choose_reinforcement.rein_id)
    choose_reinforcement = [d['rein_id'] for d in choose_reinforcement.as_list()]
    choose_hardware = db(db.choose_hardware.product_in_quotation_id == product_id).select(db.choose_hardware.hardware_id)
    choose_hardware = [d['hardware_id'] for d in choose_hardware.as_list()]
    choose_glass = db(db.choose_glass.product_in_quotation_id == product_id).select(db.choose_glass.glas_id)
    choose_glass = [d['glas_id'] for d in choose_glass.as_list()]
    choose_material = db(db.choose_material.product_in_quotation_id == product_id).select(db.choose_material.material_id)
    choose_material = [d['material_id'] for d in choose_material.as_list()]
    choose_extra = db(db.choose_extra.product_in_quotation_id == product_id).select(db.choose_extra.extra_info_id)
    choose_extra = [d['extra_info_id'] for d in choose_extra.as_list()]

    profile_names = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
    temp = {}
    for i in profile_names:
        try:
            temp[i.profile.id]
        except:
            temp[i.profile.id] = i
    profile_names = temp.values()
    reinforcement_names = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
    temp = {}
    for i in reinforcement_names:
        try:
            temp[i.reinforcement.id]
        except:
            temp[i.reinforcement.id] = i
    reinforcement_names = temp.values()
    HAA_names = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))
    temp = {}
    for i in HAA_names:
        try:
            temp[i.hardware_and_accessories.id]
        except:
            temp[i.hardware_and_accessories.id] = i
    HAA_names = temp.values()
    glass_names = db(db.glass_used_in_design.design_id == design_id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
    temp = {}
    for i in glass_names:
        try:
            temp[i.glass.id]
        except:
            temp[i.glass.id] = i
    glass_names = temp.values()
    material_names = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
    temp = {}
    for i in material_names:
        try:
            temp[i.installation_material.id]
        except:
            temp[i.installation_material.id] = i
    material_names = temp.values()
    extra_table = db(db.product_quotation_extra_information_values.product_in_quotation_id == product_id).select(join = db.product_quotation_extra_information_values.on(db.extra_information_in_design.id == db.product_quotation_extra_information_values.extra_information_in_design_id))
    temp = {}
    for i in extra_table:
        try:
            temp[i.extra_information_in_design.id]
        except:
            temp[i.extra_information_in_design.id] = i
    extra_table = temp.values()
    return dict(product=product, document=document, project_id=project_id, parameter_table=parameter_table, profile_names=profile_names, reinforcement_names=reinforcement_names, HAA_names=HAA_names, glass_names=glass_names, material_names=material_names, extra_table=extra_table, choose_params=choose_params, choose_profile=choose_profile, choose_reinforcement=choose_reinforcement, choose_hardware=choose_hardware, choose_glass=choose_glass, choose_material = choose_material, choose_extra=choose_extra)

@auth.requires_login()
def update_quotation_parameters():
    params = request.vars.parameter
    profiles = request.vars.profile
    reinforcements = request.vars.reinforcement
    haas = request.vars.hardware
    glasses = request.vars.glass
    materials = request.vars.material
    extras = request.vars.extra
    product_id = request.vars.product_id

    #Deleting entries
    parameter_table = db(db.choose_design_parameters.product_in_quotation_id == product_id).select()
    for i in parameter_table:
        i.delete_record()
    profile_table = db(db.choose_profile.product_in_quotation_id == product_id).select()
    for i in profile_table:
        i.delete_record()
    reinforcement_table = db(db.choose_reinforcement.product_in_quotation_id == product_id).select()
    for i in reinforcement_table:
        i.delete_record()
    HAA_table = db(db.choose_hardware.product_in_quotation_id == product_id).select()
    for i in HAA_table:
        i.delete_record()
    glass_table = db(db.choose_glass.product_in_quotation_id == product_id).select()
    for i in glass_table:
        i.delete_record()
    material_table = db(db.choose_material.product_in_quotation_id == product_id).select()
    for i in material_table:
        i.delete_record()
    extra_info_table = db(db.choose_extra.product_in_quotation_id == product_id).select()
    for i in extra_info_table:
        i.delete_record()

    #Adding new entries
    if params != None:
        if type(params) is not ListType:
            temp = params
            params = []
            params.append(temp)
        for i in params:
            db.choose_design_parameters.insert(product_in_quotation_id = product_id, param_id = i)
    if profiles != None:
        if type(profiles) is not ListType:
            temp = profiles
            profiles = []
            profiles.append(temp)
        for i in profiles:
            db.choose_profile.insert(product_in_quotation_id = product_id, pro_id = i)
    if reinforcements != None:
        if type(reinforcements) is not ListType:
            temp = reinforcements
            reinforcements = []
            reinforcements.append(temp)
        for i in reinforcements:
            db.choose_reinforcement.insert(product_in_quotation_id = product_id, rein_id = i)
    if haas != None:
        if type(haas) is not ListType:
            temp = haas
            haas = []
            haas.append(temp)
        for i in haas:
            db.choose_hardware.insert(product_in_quotation_id = int(product_id), hardware_id = int(i))
    if glasses != None:
        if type(glasses) is not ListType:
            temp = glasses
            glasses = []
            glasses.append(temp)
        for i in glasses:
            db.choose_glass.insert(product_in_quotation_id = int(product_id), glas_id = int(i))
    if materials != None:
        if type(materials) is not ListType:
            temp = materials
            materials = []
            materials.append(temp)
        for i in materials:
            db.choose_material.insert(product_in_quotation_id = product_id, material_id = i)
    if extras != None:
        if type(extras) is not ListType:
            temp = extras
            extras = []
            extras.append(temp)
        for i in extras:
            db.choose_extra.insert(product_in_quotation_id = product_id, extra_info_id = i)
    redirect(URL('view_quotation_product.html',vars = dict(entry_id = product_id)))
    return dict()

@auth.requires_login()
def tax_discount():
    document_id = request.vars.document_id
    return dict(document_id = document_id)

@auth.requires_login()
def generate_quotation():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    FIRST_TOP_MARGIN = 5
    TOP_MARGIN = 7
    FONT_SIZE = 14
    IMAGE_WIDTH = 185
    IMAGE_HEIGHT = 25
    HEADER_WIDTH = 185
    HEADER_HEIGHT = 7
    HEADER_DETAILS_HEIGHT = 25
    MAIN_BORDER_SIZE = 0.1
    SMALL_FONT_SIZE = 11
    DETAILS_FONT_SIZE = 9.5
    GENERIC_CONTENT_HEIGHT = 25
    PRODUCT_HEADER_HEIGHT = 7
    PRODUCT_TABLE_WIDTH = 185
    PRODUCT_TABLE_HEIGHT = 110
    PRODUCT2_TABLE_HEIGHT = 110
    PRODUCT_TABLE_START_X = 10
    PRODUCT_TABLE_START_Y = 132
    PRODUCT2_TABLE_START_Y = TOP_MARGIN
    DETAILS_X = 50
    DETAILS_VALUES_X = 75
    QTY_X = 120
    RATE_X = 140
    AMOUNT_X = 165
    DESIGN_IMAGE_WIDTH = 35
    DESIGN_IMAGE_HEIGHT = 40
    LINE_WIDTH = 4
    FINAL_TABLE_HEIGHT = 20
    FINAL_TABLE_START_X = 90
    FINAL_TABLE_WIDTH = PRODUCT_TABLE_WIDTH - FINAL_TABLE_START_X + 10
    RUPEE_X = 145
    FINAL_VALUES_X = 172
    NUM_PRODUCTS_PER_PAGE = 2

    document_id = request.vars.document_id
    tax = request.vars.tax
    discount = int(request.vars.discount)
    cst = request.vars.cst
    cst_check = request.vars.cst_check
    total_tax = float(tax)
    if cst_check != None:
        total_tax += float(cst)
    document = db(db.documents.id == document_id).select()[0]
    project = db(db.project.id == document.project_id).select()[0]
    org = db(db.organization.id == project.organization_id).select()[0]
    products = db(db.product_in_quotation.document_id == document_id).select()
    class PDF(FPDF):
        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(LEFT_MARGIN, FIRST_TOP_MARGIN, RIGHT_MARGIN)
    pdf.set_font('Times', '', FONT_SIZE)
    pdf.image(x = 10, y = FIRST_TOP_MARGIN+2, name = './applications/Prime/static/images/letter_head.jpeg', w = IMAGE_WIDTH, h = IMAGE_HEIGHT)
    pdf.set_xy(158,32)
    pdf.write(5,str(datetime.date.today().strftime('Date : %d-%m-%Y')))
    pdf.set_xy(10,32)
    pdf.write(5,'Quote No: ' + str(document.name))
    pdf.set_xy(85,32)
    pdf.write(5, 'Email: sales@primeupvc.com')

    #Header Box
    pdf.set_fill_color(128,128,128)
    pdf.set_xy(10,43)
    pdf.set_line_width(MAIN_BORDER_SIZE)
    pdf.set_text_color(255,255,255)
    pdf.set_font('Times', 'B', FONT_SIZE)
    pdf.cell(w = HEADER_WIDTH, h = HEADER_HEIGHT,border = 1,fill = 1,txt = 'To',align = 'L')
    pdf.set_xy(100,44)
    pdf.write(5, 'Deliver to')
    pdf.set_xy(10,50)
    pdf.set_text_color(0,0,0)
    pdf.cell(w = HEADER_WIDTH/2, h = HEADER_DETAILS_HEIGHT,border = 'BL')
    pdf.set_xy(10,50)
    pdf.set_font_size(SMALL_FONT_SIZE)
    pdf.multi_cell(w = HEADER_WIDTH/2, h = HEADER_DETAILS_HEIGHT/5,border = 0,fill = 0,txt = 'Name: ' + org.name + '\nAddress: ' + org.address,align = 'L')
    pdf.set_xy(10+HEADER_WIDTH/2,50)
    pdf.set_font('Times', '', FONT_SIZE)
    pdf.cell(w = HEADER_WIDTH/2+1, h = HEADER_DETAILS_HEIGHT,border = 'BR')
    pdf.set_xy(10+HEADER_WIDTH/2,50)
    pdf.set_font_size(SMALL_FONT_SIZE)
    pdf.multi_cell(w = HEADER_WIDTH/2, h = HEADER_DETAILS_HEIGHT/5,border = 0,fill = 0,txt = project.address,align = 'L')
    pdf.set_font_size(FONT_SIZE)

    #Generic Content
    pdf.set_xy(10,78)
    pdf.write(5,'To,\n')
    pdf.set_xy(10,83)
    pdf.write(5,org.name + ',\n')
    pdf.set_xy(10,93)
    pdf.set_font_size(SMALL_FONT_SIZE)
    pdf.write(5,'Sub: Offer for supply of PRIME uPVC Doors & Windows')
    pdf.set_xy(10,102)
    pdf.multi_cell(w = HEADER_WIDTH,h=GENERIC_CONTENT_HEIGHT/4.5,align = 'L', txt = 'This is in reference to the discussion with your good selves, with regard to your requirement of PRIME uPVC windows for your prestigious project. We take this opportunity to introduce ourselves as manufacturer and supplier of PRIME uPVC doors and windows. It would be our pleasure to serve and associate with your esteemed origination.')
    pdf.set_xy(10,120)
    pdf.write(5,'We are pleased to submit our best offer for the following items.')

    #First Product
    count = 0
    total = 0
    total_area = 0
    if len(products) > 0:
        design = db(db.design.id == products[0].design_id).select()[0]
        product_id = products[0].id
        choose_params = db(db.choose_design_parameters.product_in_quotation_id == product_id).select()
        params = []
        product_width = None
        product_height = None
        for i in choose_params:
            temp = db((db.product_quotation_parameter_values.design_parameter_id == i.param_id) & (db.product_quotation_parameter_values.product_in_quotation_id == product_id)).select(join = db.product_quotation_parameter_values.on(db.design_parameters.id == db.product_quotation_parameter_values.design_parameter_id))
            params.append(temp[0])
            if temp[0].design_parameters.name.lower() == 'width':
                product_width = temp[0].product_quotation_parameter_values.parameter_value
            elif temp[0].design_parameters.name.lower() == 'height':
                product_height = temp[0].product_quotation_parameter_values.parameter_value
        choose_profile = db(db.choose_profile.product_in_quotation_id == product_id).select(join = db.choose_profile.on(db.profile.id == db.choose_profile.pro_id))
        choose_reinforcement = db(db.choose_reinforcement.product_in_quotation_id == product_id).select(join = db.choose_reinforcement.on(db.reinforcement.id == db.choose_reinforcement.rein_id))
        choose_hardware = db(db.choose_hardware.product_in_quotation_id == product_id).select(join = db.choose_hardware.on(db.hardware_and_accessories.id == db.choose_hardware.hardware_id))
        choose_glass = db(db.choose_glass.product_in_quotation_id == product_id).select(join = db.choose_glass.on(db.glass.id == db.choose_glass.glas_id))
        choose_material = db(db.choose_material.product_in_quotation_id == product_id).select(join = db.choose_material.on(db.installation_material.id == db.choose_material.material_id))
        choose_extra = db(db.choose_extra.product_in_quotation_id == product_id).select()
        extra = []
        for i in choose_extra:
            temp = db(db.product_quotation_extra_information_values.extra_information_in_design_id == i.extra_info_id).select(join = db.product_quotation_extra_information_values.on(db.extra_information_in_design.id == db.product_quotation_extra_information_values.extra_information_in_design_id))
            extra.append(temp[0])
        glass_names = {}
        for gl in choose_glass:
            try:
                glass_names[gl.glass.name]
            except:
                glass_names[gl.glass.name] = 1
        glass_names = ','.join(glass_names.keys())

        #Header
        pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT_TABLE_START_Y)
        pdf.set_fill_color(128,128,128)
        pdf.set_text_color(255,255,255)
        pdf.set_font('Times', 'B', FONT_SIZE)
        pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT_HEADER_HEIGHT,border = 1,fill = 1,txt = 'Sales Line',align = 'L')
        pdf.set_xy(DETAILS_X,PRODUCT_TABLE_START_Y+1)
        pdf.write(5, 'Details')
        pdf.set_xy(QTY_X,PRODUCT_TABLE_START_Y+1)
        pdf.write(5, 'Qty')
        pdf.set_xy(RATE_X,PRODUCT_TABLE_START_Y+1)
        pdf.write(5, 'Rate(Rs.)')
        pdf.set_xy(AMOUNT_X,PRODUCT_TABLE_START_Y+1)
        pdf.write(5, 'Amount(Rs.)')
        pdf.set_text_color(0,0,0)
        pdf.set_font('Times', '', SMALL_FONT_SIZE)
        pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT_TABLE_START_Y+PRODUCT_HEADER_HEIGHT)
        pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT_HEADER_HEIGHT,border = 'BLR',fill = 0,txt = str(1),align = 'L')

        #Header Details and Image
        pdf.set_xy(DETAILS_X,PRODUCT_TABLE_START_Y+PRODUCT_HEADER_HEIGHT+1)
        pdf.write(5, products[0].name)
        pdf.set_xy(10,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT)
        pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT_TABLE_HEIGHT, border='BLR')
        pdf.set_xy(12,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.image('./applications/Prime/uploads/' + design.design_image,w = DESIGN_IMAGE_WIDTH,h = DESIGN_IMAGE_HEIGHT)

        #Product Details
        pdf.set_xy(DETAILS_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.set_font_size(DETAILS_FONT_SIZE)
        pdf.multi_cell(w=QTY_X-DETAILS_X-5, h=3.25, txt=design.description, border=0, align='L')
        pdf.set_x(DETAILS_X)
        pdf.write(LINE_WIDTH,'\n')
        pdf.set_x(DETAILS_X)
        pdf.write(LINE_WIDTH,str(product_width) + 'w x ' + str(product_height) + 'h (' + str(product_width*product_height) + ' sqft)\n')
        pdf.set_x(DETAILS_X)
        pdf.write(LINE_WIDTH,'Glass')
        pdf.set_x(DETAILS_VALUES_X)
        pdf.write(LINE_WIDTH,glass_names + '\n')
        for i in params:
            if i.design_parameters.name.lower() != 'width' and i.design_parameters.name.lower() != 'height':
                pdf.set_x(DETAILS_X)
                pdf.write(LINE_WIDTH,i.design_parameters.name)
                pdf.set_x(DETAILS_VALUES_X)
                pdf.write(LINE_WIDTH,str(i.product_quotation_parameter_values.parameter_value) + '\n')
        for i in extra:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.extra_information_in_design.name)
            pdf.set_x(DETAILS_VALUES_X)
            if i.product_quotation_extra_information_values.default_value:
                pdf.write(LINE_WIDTH,str(i.product_quotation_extra_information_values.default_value) + '\n')
            else:
                pdf.write(LINE_WIDTH,str(i.product_quotation_extra_information_values.extra_information_value) + '\n')
        for i in choose_profile:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.profile.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.profile.profile_code + '\n')
        for i in choose_hardware:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.hardware_and_accessories.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.hardware_and_accessories.description + '\n')
        for i in choose_reinforcement:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.reinforcement.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.reinforcement.description + '\n')
        for i in choose_material:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.installation_material.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.installation_material.description + '\n')

        #Qty,Rate and Amount
        pdf.line(QTY_X-5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT,QTY_X-5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT)
        pdf.line(RATE_X-5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT,RATE_X-5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT)
        pdf.line(AMOUNT_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT,AMOUNT_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT)
        pdf.set_xy(QTY_X+2,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.write(10,str(products[0].quantity))
        pdf.set_xy(RATE_X+2,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.write(10,str(round(products[0].total_value_per_piece,2)))
        pdf.set_xy(AMOUNT_X+5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+7.5)
        pdf.write(5,str(round(products[0].final_value,2)) + '\n')
        pdf.set_x(AMOUNT_X+5)
        pdf.write(5, '(' + str(round(products[0].final_value/product_width/product_height/products[0].quantity,2)) + '/sqft)\n')

        total += products[0].final_value
        count += products[0].quantity
        total_area += (product_width*product_height)*products[0].quantity

        if len(products) == 1:
            temp = total*(1-float(discount)/100)
            val = temp*(1+total_tax/100)

            #Final Table
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT)
            pdf.cell(FINAL_TABLE_WIDTH,FINAL_TABLE_HEIGHT,border='BLR')
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+1)
            pdf.set_font('Times','B',SMALL_FONT_SIZE)
            pdf.write(3,'Total\n')
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+17)
            pdf.write(3,'Grand Total')
            pdf.set_xy(RUPEE_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+1)
            pdf.write(3,'Rs.\n')
            pdf.set_xy(RUPEE_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+17)
            pdf.write(3,'Rs.')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+1)
            pdf.write(3,str(round(total,2)) + '\n')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+17)
            pdf.write(3,str(round(val,2)))
            pdf.set_font('Times','',SMALL_FONT_SIZE)
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+6)
            pdf.write(3,'Discount (' + str(discount) + '%)\n')
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+11.5)
            pdf.write(3,'Excise (' + str(total_tax) + '%)\n')
            pdf.set_xy(RUPEE_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+6)
            pdf.write(3,'Rs.\n')
            pdf.set_xy(RUPEE_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+11.5)
            pdf.write(3,'Rs.\n')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+6)
            pdf.write(3,'-' + str(round(total*discount/100,2)) + '\n')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+11.5)
            pdf.write(3,'+' + str(round(temp*total_tax/100,2)) + '\n')
            pdf.line(RUPEE_X-1,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT,RUPEE_X-1,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+FINAL_TABLE_HEIGHT)
            pdf.line(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+16,PRODUCT_TABLE_START_X+PRODUCT_TABLE_WIDTH,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+16)
            pdf.set_line_width(0.5)
            pdf.line(FINAL_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+26,PRODUCT_TABLE_START_X+PRODUCT_TABLE_WIDTH,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+26)
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+1)
            pdf.write(2,'Total Area* : ' + str(round(total_area,2)) + '\n')
            pdf.set_xy(DETAILS_X+5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+1)
            pdf.write(2,'Total Units : ' + str(round(count,2)) + '\n')
            pdf.set_xy(PRODUCT_TABLE_START_X+5,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+7)
            pdf.write(2,'Average Price : ' + str(round(val/total_area,2)) + '/sqft\n')
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+PRODUCT_TABLE_HEIGHT+18.5)
            pdf.set_font_size(DETAILS_FONT_SIZE-3)
            pdf.write(2,'*The area calculation will be accurate only for simple rectangular frames')

    else:
        pdf.set_xy(60,140)
        pdf.set_font('Times', 'B', FONT_SIZE+4)
        pdf.write(10, 'No Products added to quotation')
        pdf.set_xy(60,140)

    rem = 2
    for j in range(1,len(products)):
        if j%NUM_PRODUCTS_PER_PAGE == 1:
            pdf.add_page()
            pdf.set_font('Times', '', FONT_SIZE)
            pdf.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
            pdf.set_xy(158,TOP_MARGIN+2)
            pdf.write(5,str(datetime.date.today().strftime('Date : %d-%m-%Y')))
            pdf.set_xy(10,TOP_MARGIN+2)
            pdf.write(5,'Quote No: ' + str(document.name))
            pdf.set_xy(85,TOP_MARGIN+2)
            pdf.write(5, 'Email: sales@primeupvc.com')
            PRODUCT2_TABLE_START_Y = TOP_MARGIN+12
            rem = 2

            #Header
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT2_TABLE_START_Y)
            pdf.set_fill_color(128,128,128)
            pdf.set_text_color(255,255,255)
            pdf.set_font('Times', 'B', FONT_SIZE)
            pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT_HEADER_HEIGHT,border = 1,fill = 1,txt = 'Sales Line',align = 'L')
            pdf.set_xy(DETAILS_X,PRODUCT2_TABLE_START_Y+1)
            pdf.write(5, 'Details')
            pdf.set_xy(QTY_X,PRODUCT2_TABLE_START_Y+1)
            pdf.write(5, 'Qty')
            pdf.set_xy(RATE_X,PRODUCT2_TABLE_START_Y+1)
            pdf.write(5, 'Rate(Rs.)')
            pdf.set_xy(AMOUNT_X,PRODUCT2_TABLE_START_Y+1)
            pdf.write(5, 'Amount(Rs.)')
            pdf.set_text_color(0,0,0)
            pdf.set_font('Times', '', SMALL_FONT_SIZE)
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT2_TABLE_START_Y+PRODUCT_HEADER_HEIGHT)
            pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT_HEADER_HEIGHT,border = 1,fill = 0,txt = str(j+1),align = 'L')
        else:
            rem = 1
            PRODUCT2_TABLE_START_Y += PRODUCT2_TABLE_HEIGHT
            pdf.set_font('Times', '', SMALL_FONT_SIZE)
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT2_TABLE_START_Y+PRODUCT_HEADER_HEIGHT)
            pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT_HEADER_HEIGHT,border = 1,fill = 0,txt = str(j+1),align = 'L')

        design = db(db.design.id == products[j].design_id).select()[0]
        product_id = products[j].id
        choose_params = db(db.choose_design_parameters.product_in_quotation_id == product_id).select()
        params = []
        product_width = None
        product_height = None
        for i in choose_params:
            temp = db((db.product_quotation_parameter_values.design_parameter_id == i.param_id) & (db.product_quotation_parameter_values.product_in_quotation_id == product_id)).select(join = db.product_quotation_parameter_values.on(db.design_parameters.id == db.product_quotation_parameter_values.design_parameter_id))
            params.append(temp[0])
            if temp[0].design_parameters.name.lower() == 'width':
                product_width = temp[0].product_quotation_parameter_values.parameter_value
            elif temp[0].design_parameters.name.lower() == 'height':
                product_height = temp[0].product_quotation_parameter_values.parameter_value
        choose_profile = db(db.choose_profile.product_in_quotation_id == product_id).select(join = db.choose_profile.on(db.profile.id == db.choose_profile.pro_id))
        choose_reinforcement = db(db.choose_reinforcement.product_in_quotation_id == product_id).select(join = db.choose_reinforcement.on(db.reinforcement.id == db.choose_reinforcement.rein_id))
        choose_hardware = db(db.choose_hardware.product_in_quotation_id == product_id).select(join = db.choose_hardware.on(db.hardware_and_accessories.id == db.choose_hardware.hardware_id))
        choose_glass = db(db.choose_glass.product_in_quotation_id == product_id).select(join = db.choose_glass.on(db.glass.id == db.choose_glass.glas_id))
        choose_material = db(db.choose_material.product_in_quotation_id == product_id).select(join = db.choose_material.on(db.installation_material.id == db.choose_material.material_id))
        choose_extra = db(db.choose_extra.product_in_quotation_id == product_id).select()
        extra = []
        for i in choose_extra:
            temp = db((db.product_quotation_extra_information_values.extra_information_in_design_id == i.extra_info_id) & (db.product_quotation_extra_information_values.product_in_quotation_id == product_id)).select(join = db.product_quotation_extra_information_values.on(db.extra_information_in_design.id == db.product_quotation_extra_information_values.extra_information_in_design_id))
            extra.append(temp[0])
        glass_names = {}
        for gl in choose_glass:
            try:
                glass_names[gl.glass.name]
            except:
                glass_names[gl.glass.name] = 1
        glass_names = ','.join(glass_names.keys())

        #Header Details and Image
        pdf.set_xy(DETAILS_X,PRODUCT2_TABLE_START_Y+PRODUCT_HEADER_HEIGHT+1)
        pdf.write(5, products[j].name)
        pdf.set_xy(10,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT)
        pdf.cell(w = PRODUCT_TABLE_WIDTH, h = PRODUCT2_TABLE_HEIGHT, border='BLR')
        pdf.set_xy(12,PRODUCT2_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.image('./applications/Prime/uploads/' + design.design_image,w = DESIGN_IMAGE_WIDTH,h = DESIGN_IMAGE_HEIGHT)

        #Product Details
        pdf.set_xy(DETAILS_X,PRODUCT2_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.set_font_size(DETAILS_FONT_SIZE)
        pdf.multi_cell(w=QTY_X-DETAILS_X-5, h=3.25, txt=design.description, border=0, align='L')
        pdf.set_x(DETAILS_X)
        pdf.write(LINE_WIDTH,'\n')
        pdf.set_x(DETAILS_X)
        pdf.write(LINE_WIDTH,str(product_width) + 'w x ' + str(product_height) + 'h (' + str(product_width*product_height) + ' sqft)\n')
        pdf.set_x(DETAILS_X)
        pdf.write(LINE_WIDTH,'Glass')
        pdf.set_x(DETAILS_VALUES_X)
        pdf.write(LINE_WIDTH,glass_names + '\n')
        for i in params:
            if i.design_parameters.name.lower() != 'width' and i.design_parameters.name.lower() != 'height':
                pdf.set_x(DETAILS_X)
                pdf.write(LINE_WIDTH,i.design_parameters.name)
                pdf.set_x(DETAILS_VALUES_X)
                pdf.write(LINE_WIDTH,str(i.product_quotation_parameter_values.parameter_value) + '\n')
        for i in extra:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.extra_information_in_design.name)
            pdf.set_x(DETAILS_VALUES_X)
            if i.product_quotation_extra_information_values.default_value:
                pdf.write(LINE_WIDTH,str(i.product_quotation_extra_information_values.default_value) + '\n')
            else:
                pdf.write(LINE_WIDTH,str(i.product_quotation_extra_information_values.extra_information_value) + '\n')
        for i in choose_profile:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.profile.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.profile.profile_code + '\n')
        for i in choose_hardware:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.hardware_and_accessories.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.hardware_and_accessories.description + '\n')
        for i in choose_reinforcement:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.reinforcement.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.reinforcement.description + '\n')
        for i in choose_material:
            pdf.set_x(DETAILS_X)
            pdf.write(LINE_WIDTH,i.installation_material.name)
            pdf.set_x(DETAILS_VALUES_X)
            pdf.write(LINE_WIDTH,i.installation_material.description + '\n')

        #Qty,Rate and Amount
        pdf.line(QTY_X-5,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT,QTY_X-5,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT)
        pdf.line(RATE_X-5,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT,RATE_X-5,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT)
        pdf.line(AMOUNT_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT,AMOUNT_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT)
        pdf.set_xy(QTY_X+2,PRODUCT2_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.write(10,str(products[j].quantity))
        pdf.set_xy(RATE_X+2,PRODUCT2_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+5)
        pdf.write(10,str(round(products[j].total_value_per_piece,2)))
        pdf.set_xy(AMOUNT_X+5,PRODUCT2_TABLE_START_Y+2*PRODUCT_HEADER_HEIGHT+7.5)
        pdf.write(5,str(round(products[j].final_value,2)) + '\n')
        pdf.set_x(AMOUNT_X+5)
        pdf.write(5, '(' + str(round(products[j].final_value/product_width/product_height/products[j].quantity,2)) + '/sqft)\n')

        total += products[j].final_value
        count += products[j].quantity
        total_area += (product_width*product_height)*products[j].quantity

        if j == len(products) - 1:
            temp = total*(1-float(discount)/100)
            val = temp*(1+total_tax/100)
            FINAL_TABLE_HEIGHT = 25

            #Final Table
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT)
            pdf.cell(FINAL_TABLE_WIDTH,FINAL_TABLE_HEIGHT,border='BLR')
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+2)
            pdf.set_font('Times','B',SMALL_FONT_SIZE)
            pdf.write(3,'Total\n')
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+21.5)
            pdf.write(3,'Grand Total')
            pdf.set_xy(RUPEE_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+2)
            pdf.write(3,'Rs.\n')
            pdf.set_xy(RUPEE_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+21.5)
            pdf.write(3,'Rs.')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+2)
            pdf.write(3,str(round(total,2)) + '\n')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+21.5)
            pdf.write(3,str(round(val,2)))
            pdf.set_font('Times','',SMALL_FONT_SIZE)
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+8)
            pdf.write(3,'Discount (' + str(discount) + '%)\n')
            pdf.set_xy(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+15)
            pdf.write(3,'Excise (' + str(total_tax) + '%)\n')
            pdf.set_xy(RUPEE_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+8)
            pdf.write(3,'Rs.\n')
            pdf.set_xy(RUPEE_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+15)
            pdf.write(3,'Rs.\n')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+8)
            pdf.write(3,'-' + str(round(total*discount/100,2)) + '\n')
            pdf.set_xy(FINAL_VALUES_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+15)
            pdf.write(3,'+' + str(round(temp*total_tax/100,2)) + '\n')
            pdf.line(RUPEE_X-1,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT,RUPEE_X-1,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+FINAL_TABLE_HEIGHT)
            pdf.line(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+20,PRODUCT_TABLE_START_X+PRODUCT_TABLE_WIDTH,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+20)
            pdf.set_line_width(0.5)
            pdf.line(FINAL_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+27,PRODUCT_TABLE_START_X+PRODUCT_TABLE_WIDTH,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+27)
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+4)
            pdf.write(2,'Total Area* : ' + str(round(total_area,2)) + '\n')
            pdf.set_xy(DETAILS_X+5,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+4)
            pdf.write(2,'Total Units : ' + str(round(count,2)) + '\n')
            pdf.set_xy(PRODUCT_TABLE_START_X+5,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+10)
            pdf.write(2,'Average Price : ' + str(round(val/total_area,2)) + '/sqft\n')
            pdf.set_xy(PRODUCT_TABLE_START_X,PRODUCT2_TABLE_START_Y+rem*PRODUCT_HEADER_HEIGHT+PRODUCT2_TABLE_HEIGHT+25)
            pdf.set_font_size(DETAILS_FONT_SIZE-3)
            pdf.write(2,'*The area calculation will be accurate only for simple rectangular frames')

    #Last Page
    pdf.add_page()
    pdf.set_margins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN)
    pdf.set_xy(10,5+TOP_MARGIN)
    pdf.set_font('Times', 'BU', FONT_SIZE)
    pdf.write(10,'Excise duty and Charges')
    pdf.set_font('Times', '', SMALL_FONT_SIZE)
    pdf.set_xy(10,15+TOP_MARGIN)
    pdf.multi_cell(w = HEADER_WIDTH,h=GENERIC_CONTENT_HEIGHT/4.5,align = 'L', txt = 'The above prices are inclusive of excise duty, and freight charges at the prevailing conditions. The present rate of Excise duty is ' + str(tax) + '%. If applicable, additional CST @ ' + str(cst) + '% against form \'C\' or VAT @ ' + str(float(tax) + float(cst)) + '% is applicable. Non-submission of \'C\' Form, ' + str(tax) + '% extra, being the difference amount of CST on the quoted price will be charged. The above prices also includes installation charges.')
    pdf.set_xy(10,40+TOP_MARGIN)
    pdf.multi_cell(w = HEADER_WIDTH,h=GENERIC_CONTENT_HEIGHT/4.5,align = 'L', txt = 'ANY changes in the above rates or imposition of any new taxes, duties, octroi, etc (central or state), would be payable by you extra at actuals based on rates prevailing at the time of supply.')
    pdf.set_xy(10, 60+TOP_MARGIN)
    pdf.set_font('Times', 'BU', FONT_SIZE)
    pdf.write(10,'Terms and Conditions')
    pdf.set_font('Times', '', SMALL_FONT_SIZE)
    pdf.set_xy(10, 70+TOP_MARGIN)
    pdf.multi_cell(w = HEADER_WIDTH,h=GENERIC_CONTENT_HEIGHT/4.5,align = 'L', txt = '1.\tThe charges are according to the dimensions mentioned above. Price will change if there is any change in dimensions.')
    pdf.set_xy(10, 82+TOP_MARGIN)
    pdf.multi_cell(w = HEADER_WIDTH,h=GENERIC_CONTENT_HEIGHT/4.5,align = 'L', txt = '2.\tSite should be ready with plastering, electrical, flooring and plumbing works done for installation.')
    pdf.set_xy(10, 100+TOP_MARGIN)
    pdf.set_font('Times', '', FONT_SIZE)
    pdf.write(10,'Yours Faithfully,')
    pdf.set_font('Times', 'B', FONT_SIZE)
    pdf.set_xy(10, 105+TOP_MARGIN)
    pdf.write(10,'ECOCARE Building Innovations Pvt Ltd')
    pdf.set_xy(10, 115+TOP_MARGIN)
    pdf.write(10,'Ramesh')
    pdf.set_xy(10, 120+TOP_MARGIN)
    pdf.write(10,'Ph # +91 800 829 4345')
    pdf.set_xy(10, 125+TOP_MARGIN)
    pdf.set_text_color(71,106,52)
    pdf.set_font('Times', 'BI', FONT_SIZE)
    pdf.write(10,'Go Keen ... Go Green ...')
    pdf.set_font('Times', 'B', FONT_SIZE)
    pdf.set_text_color(0,0,0)
    pdf.set_xy(10, 130+TOP_MARGIN)
    pdf.write(10,'Office Address: Plot No. 539, Vivekananda Nagar Colony, Kukatpally, Hyderabad - 500762')
    pdf.set_xy(10, 135+TOP_MARGIN)
    pdf.write(10, 'Office Phone Number: 040 2306 6396')

    response.headers['Content-Type'] = 'application/pdf'
    filename = document.name
    pdf.output('./' + filename + '.pdf','F')
    stream = open('./' + filename + '.pdf', 'rb')
    filevalue = db.documents.document_file.store(stream, './' + filename + '.pdf')
    #db.documents.insert(project_id = project_id, name = filename, document_type = 'Production Document', document_file = filevalue,upload_time = datetime.datetime.now())
    document.document_file = filevalue
    document.upload_time = datetime.datetime.now()
    document.update_record()
    stream.close()
    os.remove('./' + filename + '.pdf')
    redirect(URL('view_docs.html', vars = dict(project_id = project.id)))
#endregion

#region Generate Production Documents
@auth.requires_login()
def generate_production_document():
    LEFT_MARGIN = 2
    RIGHT_MARGIN = 2
    TOP_MARGIN = 5
    FONT_SIZE = 11
    SMALL_FONT_SIZE = 10
    TITLE_FONT_SIZE = 15
    TEXTBOX_BORDER_SIZE = 0.5
    CELL_WIDTH = 190
    CELL_HEIGHT = 12
    TABLE1_WIDTH = 190
    TABLE1_HEIGHT = 80
    TABLE1_START_X = 10
    TABLE1_START_Y = 40
    IMAGE_WIDTH = TABLE1_WIDTH/2 - 2*TEXTBOX_BORDER_SIZE
    IMAGE_HEIGHT = TABLE1_HEIGHT - 2*TEXTBOX_BORDER_SIZE
    TABLE1_BLOCK_WIDTH = IMAGE_WIDTH/2
    TABLE1_BLOCK_HEIGHT = TABLE1_HEIGHT/16
    TABLE1_NAMES_START_X = TABLE1_START_X
    TABLE1_NAMES_START_Y = TABLE1_START_Y
    TABLE_VALS_START_X = TABLE1_START_X + TABLE1_BLOCK_WIDTH*0.8
    TABLE_VALS_START_Y = TABLE1_START_Y
    IMAGE_START_X = TABLE_VALS_START_X + TABLE1_BLOCK_WIDTH*1.2
    IMAGE_START_Y = TABLE1_START_Y
    TABLE_MIDDLE_Y = 10
    TABLE2_START_X = TABLE1_START_X
    TABLE2_START_Y = TABLE1_START_Y + TABLE1_HEIGHT + TABLE_MIDDLE_Y
    SNO_WIDTH = 10
    SNO_HEIGHT = 5
    ITEM_CODE_WIDTH = 30
    ITEM_DESC_WIDTH = 90
    QUANTITY_WIDTH =  20
    SIZE_WIDTH = 20
    CUT_WIDTH = 15
    ITEM_DESC_X = TABLE2_START_X + SNO_WIDTH
    ITEM_CODE_X = ITEM_DESC_X + ITEM_DESC_WIDTH
    QUANTITY_X = ITEM_CODE_X + ITEM_CODE_WIDTH
    SIZE_X = QUANTITY_X + QUANTITY_WIDTH
    CUT_X = SIZE_X + SIZE_WIDTH

    project_id = request.vars.project_id
    class PDF(FPDF):
        def header(self):
            self.set_font('Times', 'B', TITLE_FONT_SIZE)
            self.cell(w = 0, txt = 'PRIME uPVC DOORS AND WINDOWS', align = 'C')
            self.ln(7)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(w = 0, txt = 'Production Document', ln = 0, align = 'L')
            self.cell(w = 0, txt = str(datetime.date.today().strftime('Date : %d-%m-%Y')), align = 'R')
            self.ln(5)

        def footer(self):
            self.set_y(-10)
            self.set_font('Times', '', FONT_SIZE)
            self.cell(0, 10, 'Page %s' % self.page_no() + ' of  ' + '{nb}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()

    products = db(db.product.project_id == project_id).select()
    project = db(db.project.id == project_id).select()[0]
    docs = db((db.documents.project_id == project_id) & (db.documents.document_type == 'Production Document')).select()
    filename = 'Production_' + str(len(docs)+1)

    for i in range(len(products)):
        design = db(db.design.id == products[i].design_id).select()[0]
        block_number = products[i].block_number
        flat_number = products[i].flat_number
        window_number = products[i].window_number
        extra_comment = products[i].extra_comment
        if extra_comment == None:
            extra_comment = 'None'
        profile = db(db.profile_used_in_design.design_id == design.id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))

        parameters = db(db.design_parameters.design_id == design.id).select(join = db.design_parameters.on((db.design_parameters_values.design_parameter_id == db.design_parameters.id) & (db.design_parameters_values.product_id == products[i].id)))
        width = None
        height = None
        for entry in parameters:
            if entry.design_parameters.name.lower() == 'width':
                width = entry.design_parameters_values.parameter_value
            elif entry.design_parameters.name.lower() == 'height':
                height = entry.design_parameters_values.parameter_value

        extra_info = db(db.extra_information_in_design.design_id == design.id).select(join = db.extra_information_in_design.on((db.extra_information_values.extra_information_in_design_id == db.extra_information_in_design.id) & (db.extra_information_values.product_id == products[i].id)))
        glass = db(db.glass_used_in_design.design_id == design.id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id),orderby = db.glass.id)
        glass_names = {}
        for gl in glass:
            try:
                glass_names[gl.glass.name]
            except:
                glass_names[gl.glass.name] = 1
        glass_names = ','.join(glass_names.keys())


        fly = None
        alm = None
        handle_inner = None
        handle_outer = None
        for entry in extra_info:
            name = entry.extra_information_in_design.name.lower()
            name = name.replace(' ', '')
            name = name.replace('_', '')
            name = name.replace('-', '')
            if name == 'flyscreen':
                fly = entry.extra_information_values.default_value
            elif name == 'aluminiumtrack':
                alm = entry.extra_information_values.default_value
            elif name == 'handleinner':
                handle_inner = entry.extra_information_values.default_value
            elif name == 'handleouter':
                handle_outer = entry.extra_information_values.default_value
        if fly == None:
            fly = 'Does not apply'
        if alm == None:
            alm = 'Does not apply'
        if handle_inner == None:
            handle_inner = 'Does not apply'
        if handle_outer == None:
            handle_outer = 'Does not apply'

        pdf.add_page()
        pdf.set_font('Times', '', FONT_SIZE)

        #Heading box
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, txt='', border=1)
        pdf.set_xy(10, 25)
        pdf.cell(w=0, txt='Production Doc No :    ' + str(len(docs) + 1), ln=0, align='L')
        pdf.set_xy(120, 25)
        pdf.cell(w=0, txt='Project Name :    ' + project.name, ln=1, align='L')
        pdf.set_xy(120, 30)
        pdf.cell(w=0, txt='Document Type:    Production', ln=1, align='L')
        pdf.ln(10)

        #Product Description Table
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y)
        pdf.set_line_width(TEXTBOX_BORDER_SIZE)
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Location', border=1, align='L')
        num = 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Design', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=4 * TABLE1_BLOCK_HEIGHT, txt='Design Description', border=1, align='L')
        num += 4
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Size', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Glass', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Fly screen', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Aluminium track', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Handle Inner', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h=TABLE1_BLOCK_HEIGHT, txt='Handle Outer', border=1, align='L')
        num += 1
        pdf.set_xy(TABLE1_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*0.8, h= 4 * TABLE1_BLOCK_HEIGHT, txt='Comments', border=1, align='L')

        num = 0
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=str(block_number)+'/'+str(flat_number)+'/'+str(window_number), border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=design.name, border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h= 4*TABLE1_BLOCK_HEIGHT, border=1, align='C')
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT) + 1)
        pdf.set_font('Times', '', SMALL_FONT_SIZE)
        pdf.multi_cell(w=TABLE1_BLOCK_WIDTH*1.2, h= 0.8*TABLE1_BLOCK_HEIGHT, txt=design.description, border=0, align='C')
        pdf.set_font('Times', '', FONT_SIZE)
        num += 4
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=str(width) + ' x '+ str(height), border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=glass_names, border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=fly, border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=alm, border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=handle_inner, border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h=TABLE1_BLOCK_HEIGHT, txt=handle_outer, border=1, align='C')
        num += 1
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT))
        pdf.cell(w=TABLE1_BLOCK_WIDTH*1.2, h= 4*TABLE1_BLOCK_HEIGHT, border=1, align='C')
        pdf.set_xy(TABLE_VALS_START_X, TABLE1_START_Y + num*(TABLE1_BLOCK_HEIGHT) + 1)
        pdf.set_font('Times', '', SMALL_FONT_SIZE)
        pdf.multi_cell(w=TABLE1_BLOCK_WIDTH*1.2, h= 0.8*TABLE1_BLOCK_HEIGHT, txt=extra_comment, border=0, align='C')
        pdf.set_font('Times', '', FONT_SIZE)
        num += 4

        #Image
        pdf.set_xy(IMAGE_START_X, IMAGE_START_Y)
        pdf.cell(w=TABLE1_WIDTH/2,h=TABLE1_HEIGHT,border=1,align='C')
        pdf.set_xy(IMAGE_START_X + TEXTBOX_BORDER_SIZE, IMAGE_START_Y + TEXTBOX_BORDER_SIZE)
        pdf.image('./applications/Prime/uploads/' + design.design_image, w = IMAGE_WIDTH, h = IMAGE_HEIGHT)

        #Profile Table Header
        pdf.set_font('Times', 'B', FONT_SIZE)
        pdf.set_xy(TABLE2_START_X, TABLE2_START_Y)
        pdf.cell(w=SNO_WIDTH, h=SNO_HEIGHT, txt='S.No', border=1, align='C')
        pdf.set_xy(ITEM_CODE_X, TABLE2_START_Y)
        pdf.cell(w=ITEM_CODE_WIDTH, h=SNO_HEIGHT, txt='Item Code', border='RTB', align='C')
        pdf.set_xy(ITEM_DESC_X, TABLE2_START_Y)
        pdf.cell(w=ITEM_DESC_WIDTH, h=SNO_HEIGHT, txt='Item Description', border='RTB', align='C')
        pdf.set_xy(QUANTITY_X, TABLE2_START_Y)
        pdf.cell(w=QUANTITY_WIDTH, h=SNO_HEIGHT, txt='Quantity', border='RTB', align='C')
        pdf.set_xy(SIZE_X, TABLE2_START_Y)
        pdf.cell(w=SIZE_WIDTH, h=SNO_HEIGHT, txt='Size', border='RTB', align='C')
        pdf.set_xy(CUT_X, TABLE2_START_Y)
        pdf.cell(w=CUT_WIDTH, h=SNO_HEIGHT, txt='Cut', border='RTB', align='C')

        for j in range(len(profile)):
            profile_values = db((db.profile_values.product_id == products[i].id) & (db.profile_values.profile_used_in_design_id == profile[j].profile_used_in_design.id)).select()
            if len(profile_values) > 0:
                #Table
                POS_Y = (j+1)*SNO_HEIGHT
                pdf.set_font('Times', '', FONT_SIZE)
                pdf.set_xy(TABLE2_START_X, TABLE2_START_Y + POS_Y)
                pdf.cell(w=SNO_WIDTH, h=SNO_HEIGHT, txt=str(j+1), border=1, align='C')
                pdf.set_xy(ITEM_CODE_X, TABLE2_START_Y + POS_Y)
                pdf.cell(w=ITEM_CODE_WIDTH, h=SNO_HEIGHT, txt=profile[j].profile.profile_code, border='RTB', align='C')
                pdf.set_xy(ITEM_DESC_X, TABLE2_START_Y + POS_Y)
                pdf.cell(w=ITEM_DESC_WIDTH, h=SNO_HEIGHT, txt=profile[j].profile.description, border='RTB', align='C')
                pdf.set_xy(QUANTITY_X, TABLE2_START_Y + POS_Y)
                pdf.cell(w=QUANTITY_WIDTH, h=SNO_HEIGHT, txt=str(profile_values[0].quantity), border='RTB', align='C')
                pdf.set_xy(SIZE_X, TABLE2_START_Y + POS_Y)
                pdf.cell(w=SIZE_WIDTH, h=SNO_HEIGHT, txt=str(profile_values[0].length_value), border='RTB', align='C')
                pdf.set_xy(CUT_X, TABLE2_START_Y + POS_Y)
                pdf.cell(w=CUT_WIDTH, h=SNO_HEIGHT, txt=profile_values[0].cut, border='RTB', align='C')

    response.headers['Content-Type'] = 'application/pdf'
    pdf.output('./' + filename + '.pdf','F')
    stream = open('./' + filename + '.pdf', 'rb')
    filevalue = db.documents.document_file.store(stream, './' + filename + '.pdf')
    db.documents.insert(project_id = project_id, name = filename, document_type = 'Production Document', document_file = filevalue,upload_time = datetime.datetime.now())
    stream.close()
    os.remove('./' + filename + '.pdf')
    redirect(URL('view_docs.html', vars = dict(project_id = project_id)))

#endregion

#endregion

#region Search
#################################################################################################################
#------------------------------------------- SEARCH FUNCTION ---------------------------------------------------#
#################################################################################################################

@auth.requires_login()
def search():
    var1=request.vars.option
    var2=request.vars.search
    if(var1=="project"):
        redirect(URL('s1',vars=dict(var2=var2)))
    elif(var1=="organisation"):
        redirect(URL('s2',vars=dict(var2=var2)))
    elif(var1=="point_of_contact"):
        redirect(URL('s3',vars=dict(var2=var2)))

@auth.requires_login()
def s1():
    k=request.vars.var2
    k1=db(db.project.id>=0).select()
    l={}
    if k != "":
        for i in k1:
            if (re.search(k,str(i.name),re.IGNORECASE) or re.search(k,str(i.address),re.IGNORECASE) or re.search(k,str(i.description),re.IGNORECASE)
                or re.search(k,str(i.phase),re.IGNORECASE)):
                if i.name not in l.keys():
                    l[i.name]=i.id
    else:
        for i in k1:
                if i.name not in l.keys():
                    l[i.name]=i.id
    return dict(l=l)

@auth.requires_login()
def s2():
    k=request.vars.var2
    k1=db(db.organization.id>=0).select()
    l={}
    if k!="":
        for i in k1:
            if (re.search(k,str(i.name),re.IGNORECASE) or re.search(k,str(i.address),re.IGNORECASE)):
                sel=db(db.project.organization_id==i.id).select()
                for j in sel:
                    if j.name not in l.keys():
                        l[j.name]=j.id
    else:
        k1=db(db.project.id>=0).select()
        for i in k1:
                if i.name not in l.keys():
                    l[i.name]=i.id
    return dict(l=l)

@auth.requires_login()
def s3():
    k=request.vars.var2
    k1=db(db.point_of_contact.id>=0).select()
    l={}
    if k!="":
        for i in k1:
            if (re.search(k,str(i.name),re.IGNORECASE) or re.search(k,str(i.email),re.IGNORECASE) or re.search(k,str(i.phone_number),re.IGNORECASE)
                or re.search(k,str(i.designation),re.IGNORECASE)):
                sel=db(db.project_to_poc.poc_id==i.id).select()
                for j in sel:
                    query=db(db.project.id==j.project_id).select()
                    for row in query:
                        if row.name not in l.keys():
                            l[row.name]=row.id
    else:
        k1=db(db.project.id>=0).select()
        for i in k1:
                if i.name not in l.keys():
                    l[i.name]=i.id
    return dict(l=l)

#endregion

#region Product
#################################################################################################################
#------------------------------------------------ Product ------------------------------------------------------#
#################################################################################################################
#region Add Product
#------------------------------------------- Add New Product ---------------------------------------------------#
@auth.requires_login()
def add_new_product():
    project_id=request.vars.project_id
    rows=db(db.product.project_id==project_id).select(db.product.name)
    max=0
    for i in rows:
        try:
            number=int(re.search(r'\d+', i.name).group())
            if(number>max):
                max=number
        except:
            pass
    db.product.project_id.default = project_id
    db.product.name.default = 'product_' + str(max+1)
    form=SQLFORM(db.product,fields=['design_id', 'phase', 'block_number', 'flat_number', 'window_number'])
    if form.process().accepted:
        session.flash = 'accepted'
        id=form.vars.id
        redirect(URL('design_parameters', vars=dict(product_id=id)))
    elif form.errors:
           response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form=form)

@auth.requires_login()
def design_parameters():
    product_id = request.vars.product_id
    product = db(db.product.id == product_id).select()
    sel = []
    for i in product:
        sel=db(db.design_parameters.design_id == i.design_id).select()
    parameters={}
    parameters=collections.OrderedDict(sorted(parameters.items()))
    for row in sel:
        parameters[row.id]=row.name+'('+row.codename+')'
    return dict(parameters = parameters, product_id = product_id)

@auth.requires_login()
def design_parameters_values():
    product_id=request.vars.product_id
    product = db(db.product.id == product_id).select()[0]
    project = db(db.project.id == product.project_id).select()[0]
    parameters=request.vars
    del parameters['product_id']
    parameter_value=[]
    for parameter in parameters:
        db.design_parameters_values.insert(product_id=product_id,design_parameter_id=parameter,parameter_value=parameters[parameter])
        parameter_value.append(parameters[parameter])
    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' added product ' + product.name + ' in project ' + project.name, log_time = datetime.datetime.now())
    redirect(URL('calculate_product',vars=dict(entry_id = product_id)))
    return dict()

@auth.requires_login()
def calculate_product():
    product_id = request.vars.entry_id
    flag = request.vars.flag
    product = db(db.product.id == product_id).select()[0]
    design_id = product.design_id
    project_id = product.project_id
    design_table = db(db.design.id == design_id).select()[0]
    parameter_values_table = db(db.design_parameters_values.product_id == product_id).select(orderby=db.design_parameters_values.design_parameter_id)
    parameter_value = []
    for i in parameter_values_table:
        parameter_value.append(str(i.parameter_value))

    profile_table = db(db.profile_used_in_design.design_id == design_id).select()
    if flag:
        rows = db(db.profile_values.product_id == product_id).delete()

    for i in xrange(len(profile_table)):
        #print profile_table[i].length_calculation,parameter_value
        length_value = Infix(convert(profile_table[i].length_calculation,parameter_value))
        cost_value = Infix(convert(profile_table[i].cost_calculation,parameter_value))
        db.profile_values.insert(product_id = product_id, profile_used_in_design_id = profile_table[i].id, profile_position = profile_table[i].profile_position, cut = profile_table[i].cut, length_value = length_value, quantity = profile_table[i].quantity, profile_cost = cost_value)

    reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select()
    if flag:
        rows = db(db.reinforcement_values.product_id == product_id).delete()

    for i in xrange(len(reinforcement_table)):
        #print reinforcement_table[i].length_calculation,parameter_value
        length_value = Infix(convert(reinforcement_table[i].length_calculation,parameter_value))
        cost_value = Infix(convert(reinforcement_table[i].cost_calculation,parameter_value))
        db.reinforcement_values.insert(product_id = product_id, reinforcement_used_in_design_id = reinforcement_table[i].id, length_value = length_value, quantity = reinforcement_table[i].quantity, reinforcement_cost = cost_value)

    HAA_table = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select()
    if flag:
        rows = db(db.hardware_and_accessories_values.product_id == product_id).delete()

    for i in xrange(len(HAA_table)):
        #print HAA_table[i].cost_calculation,parameter_value
        cost_value = Infix(convert(HAA_table[i].cost_calculation,parameter_value))
        db.hardware_and_accessories_values.insert(product_id = product_id, hardware_and_accessories_used_in_design_id = HAA_table[i].id, quantity = HAA_table[i].quantity, hardware_and_accessories_cost = cost_value)

    glass_table = db(db.glass_used_in_design.design_id == design_id).select()
    if flag:
        rows = db(db.glass_values.product_id == product_id).delete()

    for i in xrange(len(glass_table)):
        #print glass_table[i].width_calculation,parameter_value
        width_value = Infix(convert(glass_table[i].width_calculation,parameter_value))
        height_value = Infix(convert(glass_table[i].height_calculation,parameter_value))
        cost_value = Infix(convert(glass_table[i].cost_calculation,parameter_value))
        db.glass_values.insert(product_id = product_id, glass_used_in_design_id = glass_table[i].id, width = width_value, height = height_value, quantity = glass_table[i].quantity, glass_cost = cost_value)

    material_table = db(db.installation_material_used_in_design.design_id == design_id).select()
    if flag:
        rows = db(db.installation_material_values.product_id == product_id).delete()

    for i in xrange(len(material_table)):
        #print material_table[i].cost_calculation,parameter_value
        cost_value = Infix(convert(material_table[i].cost_calculation,parameter_value))
        db.installation_material_values.insert(product_id = product_id, installation_material_used_in_design_id = material_table[i].id, quantity = material_table[i].quantity, installation_material_cost = cost_value)

    extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()
    if flag:
        rows = db(db.extra_information_values.product_id == product_id).delete()

    for i in xrange(len(extra_information_table)):
        value = None
        if extra_information_table[i].calculation:
            #print extra_information_table[i].calculation,parameter_value
            value = Infix(convert(extra_information_table[i].calculation,parameter_value))
        db.extra_information_values.insert(product_id = product_id, extra_information_in_design_id = extra_information_table[i].id, default_value = extra_information_table[i].default_value, extra_information_value = value)

    redirect(URL('view_product.html',vars=dict(entry_id = product_id)))
    return dict()

def convert(str1,parameter_value):
    str=""
    finalstr=[0]*10
    finalstr[0]=str1
    j=0
    i=0
    while(i<(len(str1))):
        #print i
        if(str1[i]=='P'):
            str=""
            i=i+1
            while(i<len(str1) and str1[i]!='+' and str1[i]!='-' and str1[i]!='*' and str1[i]!='/' and str1[i]!='(' and str1[i]!=')'):
                str=str+str1[i]
                i=i+1
            #print str
            finalstr[j+1]=finalstr[j].replace('P'+str,parameter_value[int(str)-1])
            j=j+1
            #print finalstr
        i=i+1
    return finalstr[j]

#endregion

#region View/Edit/Copy Product
#----------------------------------------- View/Edit/Copy Product -----------------------------------------------#
"""@auth.requires_login()
def view_product():
    product_id = None
    if request.vars.entry_id:
        product_id = request.vars.entry_id
    else:
        product_id = request.args(0, cast=int)
    product = db(db.product.id == product_id).select()[0]
    design_id = product.design_id
    project_id = product.project_id
    parameter_value = request.vars.parameter_value
    if request.vars.flag:
        parameter_value = parameter_value.split(',')
    design_table = db(db.design.id == design_id).select()
    product_table = db(db.product.id == product_id).select()
    design_parameters_table = db(db.design_parameters.design_id == design_id).select()
    profile_table = db(db.profile_used_in_design.design_id == design_id).select()
    for i in xrange(len(profile_table)):
        #print profile_table[i].length_calculation,parameter_value
        length_value = Infix(convert(profile_table[i].length_calculation,parameter_value))
        profile_table[i].length_calculation=convert(profile_table[i].length_calculation,parameter_value)
        profile_table[i].length_calculation=Infix(profile_table[i].length_calculation)
        profile_table[i].cost_calculation=convert(profile_table[i].cost_calculation,parameter_value)
        profile_table[i].cost_calculation=Infix(profile_table[i].cost_calculation)
    profile_names = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
    reinforcement_table = db(db.reinforcement_used_in_design.design_id == design_id).select()
    for i in xrange(len(reinforcement_table)):
        #print reinforcement_table[i].length_calculation,parameter_value
        reinforcement_table[i].length_calculation=convert(reinforcement_table[i].length_calculation,parameter_value)
        reinforcement_table[i].length_calculation=Infix(reinforcement_table[i].length_calculation)
        reinforcement_table[i].cost_calculation=convert(reinforcement_table[i].cost_calculation,parameter_value)
        reinforcement_table[i].cost_calculation=Infix(reinforcement_table[i].cost_calculation)
    reinforcement_names = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
    HAA_table = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select()
    for i in xrange(len(HAA_table)):
        #print HAA_table[i].cost_calculation,parameter_value
        HAA_table[i].cost_calculation=convert(HAA_table[i].cost_calculation,parameter_value)
        HAA_table[i].cost_calculation=Infix(HAA_table[i].cost_calculation)
    HAA_names = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))
    glass_table = db(db.glass_used_in_design.design_id == design_id).select()
    for i in xrange(len(glass_table)):
        #print glass_table[i].width_calculation,parameter_value
        glass_table[i].width_calculation=convert(glass_table[i].width_calculation,parameter_value)
        glass_table[i].width_calculation=Infix(glass_table[i].width_calculation)
        glass_table[i].height_calculation=convert(glass_table[i].height_calculation,parameter_value)
        glass_table[i].height_calculation=Infix(glass_table[i].height_calculation)
        glass_table[i].cost_calculation=convert(glass_table[i].cost_calculation,parameter_value)
        glass_table[i].cost_calculation=Infix(glass_table[i].cost_calculation)
    glass_names = db(db.glass_used_in_design.design_id == design_id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
    material_table = db(db.installation_material_used_in_design.design_id == design_id).select()
    for i in xrange(len(material_table)):
        #print material_table[i].cost_calculation,parameter_value
        material_table[i].cost_calculation=convert(material_table[i].cost_calculation,parameter_value)
        material_table[i].cost_calculation=Infix(material_table[i].cost_calculation)
    material_names = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
    extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()
    for i in xrange(len(extra_information_table)):
        if extra_information_table[i].calculation:
            #print extra_information_table[i].calculation,parameter_value
            extra_information_table[i].calculation=convert(extra_information_table[i].calculation,parameter_value)
            extra_information_table[i].calculation=Infix(extra_information_table[i].calculation)
    return dict(project_id=project_id, parameter_value=parameter_value, product_table=product_table, design_id = design_id, design_table = design_table, design_parameters_table = design_parameters_table, profile_table = profile_table, profile_names = profile_names, reinforcement_table = reinforcement_table, reinforcement_names = reinforcement_names, HAA_table = HAA_table, HAA_names = HAA_names, glass_table = glass_table, glass_names = glass_names, material_table = material_table, material_names = material_names, extra_information_table = extra_information_table)
"""

@auth.requires_login()
def view_product():
    product_id = request.vars.entry_id
    product_table = db(db.product.id == product_id).select()
    product = product_table[0]
    design_id = product.design_id
    project_id = product.project_id
    design_table = db(db.design.id == design_id).select()

    parameter_table = db(db.design_parameters_values.product_id == product_id).select(join = db.design_parameters_values.on(db.design_parameters.id == db.design_parameters_values.design_parameter_id),orderby=db.design_parameters.id)

    profile_values = db((db.profile_values.product_id == product_id) & (db.profile_values.profile_used_in_design_id == db.profile_used_in_design.id) & (db.profile_used_in_design.profile_id == db.profile.id)).select()
    reinforcement_values = db((db.reinforcement_values.product_id == product_id) & (db.reinforcement_values.reinforcement_used_in_design_id == db.reinforcement_used_in_design.id) & (db.reinforcement_used_in_design.reinforcement_id == db.reinforcement.id)).select()
    HAA_values = db((db.hardware_and_accessories_values.product_id == product_id) & (db.hardware_and_accessories_values.hardware_and_accessories_used_in_design_id == db.hardware_and_accessories_used_in_design.id) & (db.hardware_and_accessories_used_in_design.hardware_and_accessories_id == db.hardware_and_accessories.id)).select()
    glass_values = db((db.glass_values.product_id == product_id) & (db.glass_values.glass_used_in_design_id == db.glass_used_in_design.id) & (db.glass_used_in_design.glass_id == db.glass.id)).select()
    material_values = db((db.installation_material_values.product_id == product_id) & (db.installation_material_values.installation_material_used_in_design_id == db.installation_material_used_in_design.id) & (db.installation_material_used_in_design.installation_material_id == db.installation_material.id)).select()
    extra_values = db((db.extra_information_values.product_id == product_id) & (db.extra_information_values.extra_information_in_design_id == db.extra_information_in_design.id)).select()

    # reinforcement_values = db(db.reinforcement_values.product_id == product_id).select()
    # HAA_values = db(db.hardware_and_accessories_values.product_id == product_id).select()
    # glass_values = db(db.glass_values.product_id == product_id).select()
    # material_values = db(db.installation_material_values.product_id == product_id).select()
    # extra_values = db(db.extra_information_values.product_id == product_id).select()

    profile_names = db(db.profile_used_in_design.design_id == design_id).select(join = db.profile_used_in_design.on(db.profile.id == db.profile_used_in_design.profile_id))
    reinforcement_names = db(db.reinforcement_used_in_design.design_id == design_id).select(join = db.reinforcement_used_in_design.on(db.reinforcement.id == db.reinforcement_used_in_design.reinforcement_id))
    HAA_names = db(db.hardware_and_accessories_used_in_design.design_id == design_id).select(join = db.hardware_and_accessories_used_in_design.on(db.hardware_and_accessories.id == db.hardware_and_accessories_used_in_design.hardware_and_accessories_id))
    glass_names = db(db.glass_used_in_design.design_id == design_id).select(join = db.glass_used_in_design.on(db.glass.id == db.glass_used_in_design.glass_id))
    material_names = db(db.installation_material_used_in_design.design_id == design_id).select(join = db.installation_material_used_in_design.on(db.installation_material.id == db.installation_material_used_in_design.installation_material_id))
    extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()

    return dict(product_id = product_id, project_id = project_id, parameter_table = parameter_table, product_table = product_table, design_id = design_id, design_table = design_table, profile_table = profile_values, profile_names = profile_names, reinforcement_table = reinforcement_values, reinforcement_names = reinforcement_names, HAA_table = HAA_values, HAA_names = HAA_names, glass_table = glass_values, glass_names = glass_names, material_table = material_values, material_names = material_names, extra_information_table = extra_information_table, extra_values = extra_values)

@auth.requires_login()
def update_product():
    product_phases=['Started','Production','Delivery','Installation','Completed','Cancelled']
    variables=request.vars
    product_id = variables.product_id
    product_table = db(db.product.id == product_id).select()
    product = product_table[0]
    design_id = product.design_id
    project_id = product.project_id
    project = db(db.project.id == project_id).select()[0]

    profile_values = db(db.profile_values.product_id == product_id).select()
    reinforcement_values = db(db.reinforcement_values.product_id == product_id).select()
    HAA_values = db(db.hardware_and_accessories_values.product_id == product_id).select()
    glass_values = db(db.glass_values.product_id == product_id).select()
    material_values = db(db.installation_material_values.product_id == product_id).select()
    extra_values = db(db.extra_information_values.product_id == product_id).select()
    extra_information_table = db(db.extra_information_in_design.design_id == design_id).select()

    i=0
    flag=0
    for row in product_table:
        name="product_name_"+str(i)
        row.name=variables[name]

        name="product_phase_"+str(i)
        old_phase=row.phase
        row.phase=variables[name]
        new_phase=row.phase

        old_phase_index = product_phases.index(old_phase)
        new_phase_index = product_phases.index(new_phase)
        #print "old_phase_index=",old_phase_index
        #print "new_phase_index=",new_phase_index

        if old_phase_index in [0,1,2] and new_phase_index in [3,4]:
            flag=1
        elif old_phase_index in [3,4] and new_phase_index in [0,1,2]:
            row.installed_by = None
            row.update_record()
            flag=0

        name="product_block_number_"+str(i)
        row.block_number=variables[name]

        name="product_flat_number_"+str(i)
        row.flat_number=variables[name]

        name="product_window_number_"+str(i)
        row.window_number=variables[name]

        name="product_extra_comment_"+str(i)
        row.extra_comment=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in profile_values:
        name="profile_position_"+str(i)
        row.profile_position=variables[name]

        name="profile_cut_"+str(i)
        row.cut=variables[name]

        name="profile_quantity_"+str(i)
        row.length_value=variables[name]

        name="profile_length_"+str(i)
        row.quantity=variables[name]

        name="profile_cost_"+str(i)
        row.profile_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in reinforcement_values:
        name="reinforcement_length_"+str(i)
        row.length_value=variables[name]

        name="reinforcement_quantity_"+str(i)
        row.quantity=variables[name]

        name="reinforcement_cost_"+str(i)
        row.reinforcment_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in HAA_values:
        name="HAA_quantity_"+str(i)
        row.quantity=variables[name]

        name="HAA_cost_"+str(i)
        row.hardware_and_accessories_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in glass_values:
        name="glass_width_"+str(i)
        row.width=variables[name]

        name="glass_height_"+str(i)
        row.height=variables[name]

        name="glass_quantity_"+str(i)
        row.quantity=variables[name]

        name="glass_cost_"+str(i)
        row.glass_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in material_values:
        name="material_quantity_"+str(i)
        row.quantity=variables[name]

        name="material_cost_"+str(i)
        row.installation_material_cost=variables[name]

        row.update_record()
        i=i+1

    i=0
    for row in extra_values:
        if extra_information_table[i].default_value:
            name="extra_information_calculation_"+str(i)
            row.default_value=variables[name]
        if extra_information_table[i].calculation:
            name="extra_information_calculation_"+str(i)
            row.extra_information_value=variables[name]

        row.update_record()
        i=i+1

    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' Updated product' + product.name + ' in project ' + project.name, log_time = datetime.datetime.now())
    if(flag==1):
        redirect(URL('enter_installation.html', vars = dict(product_id = product_id)))
    else:
        redirect(URL('view_product.html',vars=dict(entry_id = product_id)))

@auth.requires_login()
def update_parameters():
    product_id = request.vars.product_id
    product = db(db.product.id == product_id).select()
    sel = []
    for i in product:
        sel=db(db.design_parameters.design_id == i.design_id).select(orderby=db.design_parameters.id)
    parameters={}
    parameters=collections.OrderedDict(sorted(parameters.items()))
    for row in sel:
        parameters[row.id]=row.name+'('+row.codename+')'
    return dict(parameters = parameters, product_id = product_id)
@auth.requires_login()
def update_parameters_helper():
    product_id=request.vars.product_id
    product_parameters = db(db.design_parameters_values.product_id==product_id).select(orderby=db.design_parameters_values.design_parameter_id)
    product = db(db.product.id == product_id).select()[0]
    project = db(db.project.id == product.project_id).select()[0]
    parameters=request.vars
    del parameters['product_id']
    for param in product_parameters:
        param.delete_record()
    for parameter in parameters:
        db.design_parameters_values.insert(product_id=product_id,design_parameter_id=parameter,parameter_value=parameters[parameter])
    db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' Updated product' + product.name + ' in project ' + project.name, log_time = datetime.datetime.now())
    redirect(URL('calculate_product',vars=dict(entry_id = product_id, flag = 1)))
    return dict()

@auth.requires_login()
def change_phase():
    phase = request.vars.phase
    product_id = request.vars.product_id
    project_id = request.vars.project_id
    product = db(db.product.id == product_id).select()
    for i in product:
        project = db(db.project.id == i.project_id).select()[0]
        i.phase = phase
        i.update_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated phase of ' + i.name + ' of project ' + project.name + ' to ' + phase + ' phase', log_time = datetime.datetime.now())
    if phase == 'Installation':
        redirect(URL('enter_installation.html', vars = dict(product_id = product_id)))
    else:
        redirect(URL('view_project.html', vars = dict(project_id = project_id)))
    return dict()

@auth.requires_login()
def enter_installation():
    product_id = request.vars.product_id
    product = db(db.product.id == product_id).select()[0]
    inst_list = db(db.installation_details.id >= 0).select()
    form = SQLFORM(db.installation_details)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted installation details ' + form.vars.name, log_time = datetime.datetime.now())
        redirect(URL('add_installation_logs.html', vars=dict(product_id = product_id, install_id = form.vars.id)))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(inst_list = inst_list, form=form, product = product)
@auth.requires_login()
def add_installation_logs():
    product_id = request.vars.product_id
    install_id = request.vars.install_id
    product = db(db.product.id == product_id).select()
    project_id = product[0].project_id
    install = db(db.installation_details.id == install_id).select()[0]
    for pro in product:
        pro.installed_by = install_id
        pro.update_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' entered installation details for product ' + pro.name + ' as Name: ' + install.name + ' Phone Number: ' + install.phone_number, log_time = datetime.datetime.now())
    redirect(URL('view_project.html', vars = dict(project_id = project_id)))
    return dict()

@auth.requires_login()
def copy_details():
    product_id = request.vars.product_id
    return dict(product_id = product_id)

@auth.requires_login()
def copy_product():
    product_id = request.vars.product_id
    quantity = int(request.vars.quantity)
    product = db(db.product.id == product_id).select()[0]
    project_id = product.project_id

    parameter_values = db(db.design_parameters_values.product_id == product_id).select()
    profile_value = db(db.profile_values.product_id == product_id).select()
    reinforcement_value = db(db.reinforcement_values.product_id == product_id).select()
    HAA_value = db(db.hardware_and_accessories_values.product_id == product_id).select()
    glass_value = db(db.glass_values.product_id == product_id).select()
    material_value = db(db.installation_material_values.product_id == product_id).select()
    extra_info_value = db(db.extra_information_values.product_id == product_id).select()

    for num in range(quantity):

        #Naming Products
        rows=db(db.product.project_id==project_id).select(db.product.name)
        max=0
        for i in rows:
            try:
                number=int(re.search(r'\d+', i.name).group())
                if(number>max):
                    max=number
            except:
                pass
        name = 'product_' + str(max+1)

        #Copying Values
        new_id = db.product.insert(name = name, design_id = product.design_id, project_id = project_id, phase = product.phase, installed_by = product.installed_by,
                          block_number = product.block_number, flat_number = product.flat_number, window_number = product.window_number, extra_comment = product.extra_comment)

        for entry in parameter_values:
            db.design_parameters_values.insert(product_id = new_id, design_parameter_id = entry.design_parameter_id, parameter_value = entry.parameter_value)
        for entry in profile_value:
            db.profile_values.insert(product_id = new_id, profile_used_in_design_id = entry.profile_used_in_design_id, profile_position = entry.profile_position,
                                     cut = entry.cut, length_value = entry.length_value, quantity = entry.quantity, profile_cost = entry.profile_cost)
        for entry in reinforcement_value:
            db.reinforcement_values.insert(product_id = new_id, reinforcement_used_in_design_id = entry.reinforcement_used_in_design_id, length_value = entry.length_value, quantity = entry.quantity, reinforcement_cost = entry.reinforcement_cost)
        for entry in HAA_value:
            db.hardware_and_accessories_values.insert(product_id = new_id, hardware_and_accessories_used_in_design_id = entry.hardware_and_accessories_used_in_design_id, quantity = entry.quantity, hardware_and_accessories_cost = entry.hardware_and_accessories_cost)
        for entry in glass_value:
            db.glass_values.insert(product_id = new_id, glass_used_in_design_id = entry.glass_used_in_design_id, width = entry.width, height = entry.height, quantity = entry.quantity, glass_cost = entry.glass_cost)
        for entry in material_value:
            db.installation_material_values.insert(product_id = new_id, installation_material_used_in_design_id = entry.installation_material_used_in_design_id, quantity = entry.quantity, installation_material_cost = entry.installation_material_cost)
        for entry in extra_info_value:
            db.extra_information_values.insert(product_id = new_id, extra_information_in_design_id = entry.extra_information_in_design_id, default_value = entry.default_value, extra_information_value = entry.extra_information_value)

    redirect(URL('view_project.html', vars = dict(project_id = project_id)))
    return dict()

#endregion

#region Delete Product
#--------------------------------------------- Delete Product ---------------------------------------------------#
@auth.requires_login()
def delete_product():
    project_id = request.vars.project_id
    product_list = db((db.product.id >= 0) & (db.product.project_id == project_id)).select()
    return dict(product_list = product_list, project_id = project_id)
@auth.requires_login()
def delete_product_helper():
    project_id = request.vars.project_id
    product_list = []
    for var in request.vars:
        try:
            product_list.append(int(var))
        except:
            pass
    delete_list = db((db.product.id >= 0) & (db.product.id.belongs(product_list))).select()
    for product in delete_list:
        #Deleting Products and associated entries
        design_parameters_values_list = db(db.design_parameters_values.product_id == product.id).select()
        for parameter in design_parameters_values_list:
            parameter.delete_record()

        profile_values_list = db(db.profile_values.product_id == product.id).select()
        for profile in profile_values_list:
            profile.delete_record()

        reinforcement_values_list = db(db.reinforcement_values.product_id == product.id).select()
        for reinforcement in reinforcement_values_list:
            reinforcement.delete_record()

        hardware_and_accessories_values_list = db(db.hardware_and_accessories_values.product_id == product.id).select()
        for hardware in hardware_and_accessories_values_list:
            hardware.delete_record()

        glass_values_list = db(db.glass_values.product_id == product.id).select()
        for glass in glass_values_list:
            glass.delete_record()

        installation_material_values_list = db(db.installation_material_values.product_id == product.id).select()
        for material in installation_material_values_list:
            material.delete_record()

        extra_information_values_list = db(db.extra_information_values.product_id == product.id).select()
        for info in extra_information_values_list:
            info.delete_record()

        product_cost_list = db(db.product_cost.product_id == product.id).select()
        for cost in product_cost_list:
            cost.delete_record()
        product.delete_record()
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' removed product entry Name: ' + product.name + ' Block Number: ' + product.block_number + ' Flat Number: ' + product.flat_number + ' Window Number: ' + product.window_number + ' Phase: ' + product.phase, log_time = datetime.datetime.now())
    redirect(URL('view_project.html', vars = dict(project_id = project_id)))
    response.flash = 'Success'
    return dict()

#endregion

#region Installation
@auth.requires_login()
def add_installation_details():
    form = SQLFORM(db.installation_details)
    if form.process().accepted:
        response.flash = 'form accepted'
        db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' inserted Installation Details ' + form.vars.name, log_time = datetime.datetime.now())
        redirect(URL('index.html'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
    return dict(form = form)

@auth.requires_login()
def update_installation_details():
    Ins_id = request.vars.entry_id
    l = db(db.installation_details.id == Ins_id).select()
    form = []
    for i in l:
        old_name = i.name
        old_number = i.phone_number
        form = SQLFORM(db.installation_details, i, showid=False, deletable=False)
        if form.process().accepted:
            response.flash = 'form accepted'
            db.logs.insert(log_message='User ' + auth.user.first_name + ' ' + auth.user.last_name + ' updated Installation Details: '
                                       + old_name + ' Phone Number: ' + old_number +
                                       ' to Name: ' + form.vars.name + ' Phone Number: ' + form.vars.phone_number,
                           log_time = datetime.datetime.now())
            redirect(URL('index.html'))
        elif form.errors:
           response.flash = 'form has errors'
        else:
           response.flash = 'please update'
    return dict(form=form)

#endregion

#endregion

#region Calculation
#################################################################################################################
#------------------------------------------- Calculation -------------------------------------------------------#
#################################################################################################################

def isOp(c):
    if c != "": return (c in "+-*/")
    else: return False

def pri(c): # operator priority
    if c in "+-": return 0
    if c in "*/": return 1

def isNum(c):
    if c != "": return (c in "0123456789.")
    else: return False

def calc(op, num1, num2):
    if op == "+": return str(float(num1) + float(num2))
    if op == "-": return str(float(num1) - float(num2))
    if op == "*": return str(float(num1) * float(num2))
    if op == "/": return str(float(num1) / float(num2))

def Infix(expr):
    expr = list(expr)
    stackChr = list() # character stack
    stackNum = list() # number stack
    num = ""
    while len(expr) > 0:
        c = expr.pop(0)
        if len(expr) > 0: d = expr[0]
        else: d = ""
        if isNum(c):
            num += c
            if not isNum(d):
                stackNum.append(num)
                num = ""
        elif isOp(c):
            while True:
                if len(stackChr) > 0: top = stackChr[-1]
                else: top = ""
                if isOp(top):
                    if not pri(c) > pri(top):
                        num2 = stackNum.pop()
                        op = stackChr.pop()
                        num1 = stackNum.pop()
                        stackNum.append(calc(op, num1, num2))
                    else:
                        stackChr.append(c)
                        break
                else:
                    stackChr.append(c)
                    break
        elif c == "(":
            stackChr.append(c)
        elif c == ")":
            while len(stackChr) > 0:
                c = stackChr.pop()
                if c == "(":
                    break
                elif isOp(c):
                    num2 = stackNum.pop()
                    num1 = stackNum.pop()
                    stackNum.append(calc(c, num1, num2))

    while len(stackChr) > 0:
        c = stackChr.pop()
        if c == "(":
            break
        elif isOp(c):
            num2 = stackNum.pop()
            num1 = stackNum.pop()
            stackNum.append(calc(c, num1, num2))

    return str(round(float(stackNum.pop()),3))

#endregion

def under_construction():
    return dict()
