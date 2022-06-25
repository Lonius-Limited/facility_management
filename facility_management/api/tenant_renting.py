from functools import reduce

import frappe
from frappe.utils.data import nowdate


@frappe.whitelist()
def get_rental_listing():
    def data_occupied(rental):
        name = rental.get("name")
        return {"occupied": name in rented_properties}

    rented_properties = _get_rented_properties()
    occupied = list(map(data_occupied, _get_rental_properties()))

    return {
        "Vacant": len(list(filter(lambda x: not x["occupied"], occupied))),
        "Occupied": len(list(filter(lambda x: x["occupied"], occupied))),
    }


@frappe.whitelist()
def get_customer(tenant_renting):
    """
    Deprecated
    :param tenant_renting:
    :return:
    """
    tenant = frappe.db.get_value("Rental Contract", tenant_renting, "tenant")
    return frappe.db.get_value("Tenant Master", tenant, "customer")


def get_landlord_details(property):
    landlord = frappe.db.get_value("Property", property, "landlord")
    cpr = frappe.db.get_value("Landlord", landlord, "cpr")
    return {"name": landlord, "cpr": cpr}


def get_tenant_details(tenant):
    tenant_details = frappe.db.sql(
        """
            SELECT tenant_name, cpr, passport_no
            FROM `tabTenant Master`
            WHERE name = %(tenant)s
        """,
        {"tenant": tenant},
        as_dict=1,
    )
    return tenant_details[0] if tenant_details else None


def _get_rental_properties():
    return frappe.db.sql(
        """
            SELECT
                p.name,
                p.title,
                p.property_type
            FROM `tabProperty` p
            WHERE p.property_status = 'Rental'
        """,
        as_dict=True,
    )


def _get_rented_properties():
    def make_data(tenant_renting):
        return tenant_renting.get("property")

    return list(
        map(
            make_data,
            frappe.db.sql(
                """
                    SELECT property 
                    FROM `tabRental Contract`
                    WHERE %s BETWEEN contract_start_date AND contract_end_date
                """,
                nowdate(),
                as_dict=True,
            ),
        )
    )
@frappe.whitelist(allow_guest=True)    
def get_vacant_properties(real_estate_property=None):
    filters = dict(property_status = 'Rental',rental_status=['!=','Rented'])
    if real_estate_property:
        filters["property_group"] = real_estate_property

    fields = ['name', 'modified', 'property_group', 'property_no', 'property_floor', 'title', 'property_type', 'property_status', 'landlord', 'rental_status', 'rental_frequency', 'rental_rate', 'furnished', 'property_size', 'air_conditioning', 'bedroom', 'bathroom', 'municipality_no', 'eletric_meter_no', 'water_meter_no', 'parking', 'pets_allowed',"free_wifi", 'house_image']
    return frappe.get_all("Property", filters=filters, fields=fields)  or []

@frappe.whitelist(allow_guest=True)
def get_all_regions():
    locations = [x for x in frappe.get_all("Real Estate Property",filters=dict(location=["!=",""]),fields=["name","location"])]
    def _append_actual(obj):
        # print(obj)
        location = frappe.get_all("Location",filters=dict(name=obj.get("location")),fields=["latitude","longitude"])
        vacants = get_vacant_properties(real_estate_property=obj.get("name"))
        obj["actual"] = location
        obj["vacants"] = vacants
        return obj
    list(map(lambda x: _append_actual(x),locations))

    return locations
@frappe.whitelist(allow_guest=True)    
def get_vacant_properties_with_locations(real_estate_property=None):
    filters = dict(property_status = 'Rental',rental_status=['!=','Rented'])
    if real_estate_property:
        filters["property_group"] = real_estate_property
    fields = ['name', 'modified', 'property_group', 'property_no', 'property_floor', 'title', 'property_type', 'property_status', 'landlord', 'rental_status', 'rental_frequency', 'rental_rate', 'furnished', 'property_size', 'air_conditioning', 'bedroom', 'bathroom', 'municipality_no', 'eletric_meter_no', 'water_meter_no', 'parking', 'pets_allowed',"free_wifi", 'house_image']
    vacants = frappe.get_all("Property", filters=filters, fields=fields)  or []
    for vacant in vacants:
        location = frappe.get_value("Real Estate Property", vacant.get("property_group"),'location') or ""
        location_details = []
        if location: 
            location_details = frappe.get_all("Location",filters=dict(name=location),fields=["latitude","longitude"]) 
        vacant["location"] = location
        vacant["actual"] = location_details
        vacant["property_photographs"] = get_property_photographs(vacant.get("name"))
    return [x for x in vacants if x.get("actual")]
def get_property_photographs(property_name):
    photos = frappe.get_all("Property Photos", filters= dict(parent=property_name),fields=["photo","description"])

    if not photos: return []
 
    URL = frappe.utils.get_url()

    return list(map(lambda x: dict(description=x.get("description") or "",photo='{}/{}'.format(URL,str(x.get("photo")))), photos))