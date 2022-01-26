from typing import List, Optional

import sys
import os
import json
import yaml

import math

from .utils import Merge
from .units import load_units, convert_data

def create_params_supra(gdata: tuple, method_data: List[str], debug: bool=False) -> dict:
    """
    Return params_dict, the dictionnary of section \"Parameters\" for JSON file.
    """
    print("create_params_supra")
    
    # TODO: length data are written in mm should be in SI instead
    unit_Length = method_data[5] # "meter"
    units = load_units(unit_Length)

    # Tini, Aini for transient cases??
    params_data = { 'Parameters': []}

    if debug:
        print(params_data)
        
    return params_data

def create_params_bitter(gdata: tuple, method_data: List[str], debug: bool=False):
    """
    Return params_dict, the dictionnary of section \"Parameters\" for JSON file.
    """
    print("create_params_bitter for %s" % gdata[0])
    
    # TODO: length data are written in mm should be in SI instead
    unit_Length = method_data[5] # "meter"
    units = load_units(unit_Length)

    # Tini, Aini for transient cases??
    params_data = { 'Parameters': []}

    # for cfpdes only
    if method_data[0] == "cfpdes" and method_data[3] == "thmagel" :
        params_data['Parameters'].append({"name":"bool_laplace", "value":"1"})
        params_data['Parameters'].append({"name":"bool_dilatation", "value":"1"})

    # TODO : initialization of parameters with cooling model

    params_data['Parameters'].append({"name":"Tinit", "value":293})
    
    (name, snames, nturns) = gdata
    for sname in snames:
        params_data['Parameters'].append({"name":"%s_h" % sname, "value":convert_data(units, unit_Length, 58222.1, "h")})
        params_data['Parameters'].append({"name":"%s_Tw" % sname, "value":290.671})
        params_data['Parameters'].append({"name":"%s_dTw" % sname, "value":12.74})

    # init values for U (Axi specific)
    if method_data[2] == "Axi":
        for i,sname in enumerate(snames):
            params_data['Parameters'].append({"name":"U_%s" % sname, "value":"1"})
            params_data['Parameters'].append({"name":"N_%s" % sname, "value":nturns[i]})

    if debug:
        print(params_data)
        
    return params_data

def create_params_insert(gdata: tuple, method_data: List[str], debug: bool=False) -> dict:
    """
    Return params_dict, the dictionnary of section \"Parameters\" for JSON file.
    """
    print("create_params_insert")

    # TODO: length data are written in mm should be in SI instead
    unit_Length = method_data[5] # "meter"
    units = load_units(unit_Length)

    (NHelices, NRings, NChannels, Nsections, R1, R2, Z1, Z2, Zmin, Zmax, Dh, Sh) = gdata
    
    if debug: print("R1:", R1)
    for data in [R1, R2, Z1, Z2, Zmin, Zmax, Dh]:
        data = convert_data(units, unit_Length, data, "Length")
    Sh = convert_data(units, unit_Length, Sh, "Area")

    # chech dim
    if debug: print("corrected R1:", R1)
    
    # Tini, Aini for transient cases??
    params_data = { 'Parameters': []}

    # for cfpdes only
    if method_data[0] == "cfpdes" and method_data[3] == "thmagel" :
        params_data['Parameters'].append({"name":"bool_laplace", "value":"1"})
        params_data['Parameters'].append({"name":"bool_dilatation", "value":"1"})

    # TODO : initialization of parameters with cooling model

    params_data['Parameters'].append({"name":"Tinit", "value":293})
    params_data['Parameters'].append({"name":"h", "value":convert_data(units, unit_Length, 58222.1, "h")})
    params_data['Parameters'].append({"name":"Tw", "value":290.671})
    params_data['Parameters'].append({"name":"dTw", "value":12.74})
    
    # params per cooling channels
    # h%d, Tw%d, dTw%d, Dh%d, Sh%d, Zmin%d, Zmax%d :

    for i in range(NHelices+1):
        params_data['Parameters'].append({"name":"h%d" % i, "value":convert_data(units, unit_Length, 58222.1, "h")})
        params_data['Parameters'].append({"name":"Tw%d" % i, "value":290.671})
        params_data['Parameters'].append({"name":"dTw%d" % i, "value":12.74})
        params_data['Parameters'].append({"name":"Zmin%d" % i, "value":Zmin[i]})
        params_data['Parameters'].append({"name":"Zmax%d" % i, "value":Zmax[i]})
        params_data['Parameters'].append({"name":"Sh%d" % i, "value":Sh[i]})
        params_data['Parameters'].append({"name":"Dh%d" % i, "value":Dh[i]})

    # init values for U (Axi specific)
    if method_data[2] == "Axi":
        for i in range(NHelices):
            for j in range(Nsections[i]):
                params_data['Parameters'].append({"name":"U_H%d_Cu%d" % (i+1, j+1), "value":"1"})
        for i in range(NHelices):
            for j in range(Nsections[i]):
                params_data['Parameters'].append({"name":"N_H%d_Cu%d" % (i+1, j+1), "value":Nsections[i]})
    
    if "mag" in method_data[3] or "mqs" :
        params_data['Parameters'].append({"name":"mu0", "value":convert_data(units, unit_Length, 4*math.pi*1e-7, "mu0")})
    # TODO: CG: U_H%d%
    # TODO: HDG: U_H%d% if no ibc    # TODO: length data are written in mm should be in SI instead
    
    if debug:
        print(params_data)
        
    return params_data


def create_materials_supra(gdata: tuple, confdata: dict, templates: dict, method_data: List[str], debug: bool = False) -> dict:
    materials_dict = {}
    if debug: print("create_material_supra:", confdata)

    fconductor = templates["conductor"]
    
    # TODO: length data are written in mm should be in SI instead
    unit_Length = method_data[5] # "meter"
    units = load_units(unit_Length)
    for prop in ["ThermalConductivity", "Young", "VolumicMass", "ElectricalConductivity"]:
        confdata["material"][prop] = convert_data(units, unit_Length, confdata["material"][prop], prop)

    if method_data[2] == "Axi":
        pass
    else:
        pass

    return materials_dict

def create_materials_bitter(gdata: tuple, confdata: dict, templates: dict, method_data: List[str], debug: bool = False) -> dict:
    materials_dict = {}
    if debug: print("create_material_bitter:", confdata)

    fconductor = templates["conductor"]
    
    # TODO: length data are written in mm should be in SI instead
    unit_Length = method_data[5] # "meter"
    units = load_units(unit_Length)
    
    for prop in ["ThermalConductivity", "Young", "VolumicMass", "ElectricalConductivity"]:
        confdata["material"][prop] = convert_data(units, unit_Length, confdata["material"][prop], prop)

    (name, snames, turns) = gdata
    for sname in snames:
        if method_data[2] == "Axi":
            if debug: print("create_material_bitter:", sname)
            mdata = entry(fconductor, Merge({'name': "%s" % sname}, confdata["material"]) , debug)
            materials_dict["%s" % sname] = mdata["%s" % sname]
        else:
            return {}

    if debug:
        print(materials_dict)
    return materials_dict

def create_materials_insert(gdata: tuple, idata: Optional[List], confdata: dict, templates: dict, method_data: List[str], debug: bool = False) -> dict:
    # TODO loop for Plateau (Axi specific)
    materials_dict = {}
    if debug: print("create_material_insert:", confdata)

    fconductor = templates["conductor"]
    finsulator = templates["insulator"]

    (NHelices, NRings, NChannels, Nsections, R1, R2, Z1, Z2, Zmin, Zmax, Dh, Sh) = gdata

    # TODO: length data are written in mm should be in SI instead
    unit_Length = method_data[5] # "meter"
    units = load_units(unit_Length)
    for mtype in ["Helix", "Ring", "Lead"]:
        if mtype in confdata:
            for i in range(len(confdata[mtype])):            
                for prop in ["ThermalConductivity", "Young", "VolumicMass", "ElectricalConductivity"]:
                    confdata[mtype][i]["material"][prop] = convert_data(units, unit_Length, confdata[mtype][i]["material"][prop], prop)
            
    # Loop for Helix
    for i in range(NHelices):
        if method_data[2] == "3D":
            mdata = entry(fconductor, Merge({'name': "H%d" % (i+1), 'marker': "H%d_Cu" % (i+1)}, confdata["Helix"][i]["material"]) , debug)
            materials_dict["H%d" % (i+1)] = mdata["H%d" % (i+1)]

            if idata:
                for item in idata:
                    if item(0) == "Glue":
                        name = "Isolant%d" % (i+1)
                        mdata = entry(finsulator, Merge({'name': name, 'marker': "H%d_Isolant" % (i+1)}, confdata["Helix"][i]["insulator"]), debug)
                    else:
                        name = "Kaptons%d" % (i+1)
                        kapton_dict = { "name": "[\"Kapton%1%\"]", "index1": "0:%d" % item(1)}
                        mdata = entry(finsulator, Merge({'name': name, 'marker': kapton_dict}, confdata["Helix"][i]["insulator"]), debug)
                    materials_dict[name] = mdata[name]
        else:
            # section j==0:  treated as insulator in Axi
            mdata = entry(finsulator, Merge({'name': "H%d_Cu%d" % (i+1, 0)}, confdata["Helix"][i]["material"]), debug)
            materials_dict["H%d_Cu%d" % (i+1, 0)] = mdata["H%d_Cu%d" % (i+1, 0)]
        
            # load conductor template
            for j in range(1,Nsections[i]+1):
                # print("load conductor[%d]: mat:" % j, confdata["Helix"][i]["material"])
                mdata = entry(fconductor, Merge({'name': "H%d_Cu%d" % (i+1, j)}, confdata["Helix"][i]["material"]), debug)
                # print("load conductor[%d]:" % j, mdata)
                materials_dict["H%d_Cu%d" % (i+1, j)] = mdata["H%d_Cu%d" % (i+1, j)]

            # section j==Nsections+1:  treated as insulator in Axi
            mdata = entry(finsulator, Merge({'name': "H%d_Cu%d" % (i+1, Nsections[i]+1)}, confdata["Helix"][i]["material"]), debug)
            materials_dict["H%d_Cu%d" % (i+1, Nsections[i]+1)] = mdata["H%d_Cu%d" % (i+1, Nsections[i]+1)]

    # loop for Rings
    for i in range(NRings):
        if method_data[2] == "3D":
            mdata = entry(fconductor, Merge({'name': "R%d" % (i+1)}, confdata["Ring"][i]["material"]), debug)
        else:
            mdata = entry(finsulator, Merge({'name': "R%d" % (i+1)}, confdata["Ring"][i]["material"]), debug)
        materials_dict["R%d" % (i+1)] = mdata["R%d" % (i+1)]
        
    # Leads: 
    if method_data[2] == "3D" and confdata["Lead"]:
        mdata = entry(fconductor, Merge({'name': "iL1"}, confdata["Lead"][0]["material"]), debug)
        materials_dict["iL1"] = mdata["iL1"]

        mdata = entry(fconductor, Merge({'name': "oL2"}, confdata["Lead"][1]["material"]), debug)
        materials_dict["oL2"] = mdata["oL2"]

    return materials_dict


def create_bcs_supra(boundary_meca: List, 
               boundary_maxwell: List,
               boundary_electric: List,
               gdata: tuple, confdata: dict, templates: dict, method_data: List[str], debug: bool = False) -> dict:

    print("create_bcs_bitter from templates")
    electric_bcs_dir = { 'boundary_Electric_Dir': []} # name, value, vol
    electric_bcs_neu = { 'boundary_Electric_Neu': []} # name, value
    thermic_bcs_rob = { 'boundary_Therm_Robin': []} # name, expr1, expr2
    thermic_bcs_neu = { 'boundary_Therm_Neu': []} # name, value
    meca_bcs_dir = { 'boundary_Meca_Dir': []} # name, value
    maxwell_bcs_dir = { 'boundary_Maxwell_Dir': []} # name, value
    
    fcooling = templates["cooling"]
    
    return {}

def create_bcs_bitter(boundary_meca: List, 
               boundary_maxwell: List,
               boundary_electric: List,
               gdata: tuple, confdata: dict, templates: dict, method_data: List[str], debug: bool = False) -> dict:

    (name, snames, nturns) = gdata
    print("create_bcs_bitter from templates for %s" % name)
    # print("snames=", snames)
    
    electric_bcs_dir = { 'boundary_Electric_Dir': []} # name, value, vol
    electric_bcs_neu = { 'boundary_Electric_Neu': []} # name, value
    thermic_bcs_rob = { 'boundary_Therm_Robin': []} # name, expr1, expr2
    thermic_bcs_neu = { 'boundary_Therm_Neu': []} # name, value
    meca_bcs_dir = { 'boundary_Meca_Dir': []} # name, value
    maxwell_bcs_dir = { 'boundary_Maxwell_Dir': []} # name, value
    
    fcooling = templates["robin"]

    for sname in snames:
        for thbc in ["rInt", "rExt"]:
            bcname =  sname + "_" + thbc
            mdata = entry(fcooling, {'name': bcname, 'h': '%s_h' % sname, 'Tw': '%s_Tw' % sname, 'dTw':'%s_dTw' % sname},  debug)
            thermic_bcs_rob['boundary_Therm_Robin'].append( Merge({"name": bcname}, mdata[bcname]) )
    
    if method_data[3] == "thelec":
        th_ = Merge(thermic_bcs_rob, thermic_bcs_neu)
        if method_data[2] == "Axi":
            return th_
        else:
            return {}
    elif method_data[3] == 'mag':
        return {}
    elif method_data[3] == 'thmag':
        th_ = Merge(thermic_bcs_rob, thermic_bcs_neu)
        if method_data[2] == "Axi":
            return Merge(maxwell_bcs_dir, th_)
        else:
            return {}
    else:
        th_ = Merge(thermic_bcs_rob, thermic_bcs_neu)
        elec_ = Merge(electric_bcs_dir, electric_bcs_neu)
        thelec_ = Merge(th_, elec_)
        thelecmeca_ = Merge(thelec_, meca_bcs_dir)
        return Merge(maxwell_bcs_dir, thelecmeca_)
    
    return {}

def create_bcs_insert(boundary_meca: List, 
               boundary_maxwell: List,
               boundary_electric: List,
               gdata: tuple, confdata: dict, templates: dict, method_data: List[str], debug: bool = False) -> dict:

    print("create_bcs from templates")
    electric_bcs_dir = { 'boundary_Electric_Dir': []} # name, value, vol
    electric_bcs_neu = { 'boundary_Electric_Neu': []} # name, value
    thermic_bcs_rob = { 'boundary_Therm_Robin': []} # name, expr1, expr2
    thermic_bcs_neu = { 'boundary_Therm_Neu': []} # name, value
    meca_bcs_dir = { 'boundary_Meca_Dir': []} # name, value
    maxwell_bcs_dir = { 'boundary_Maxwell_Dir': []} # name, value
    
    (NHelices, NRings, NChannels, Nsections, R1, R2, Z1, Z2, Zmin, Zmax, Dh, Sh) = gdata
    fcooling = templates["cooling"]
    
    for i in range(NChannels):
        # load insulator template for j==0
        mdata = entry(fcooling, {'i': i}, debug)
        thermic_bcs_rob['boundary_Therm_Robin'].append( Merge({"name": "Channel%d" % i}, mdata["Channel%d" % i]) )

    for bc in boundary_meca:
        meca_bcs_dir['boundary_Meca_Dir'].append({"name":bc, "value":"{0,0}"})

    for bc in boundary_maxwell:
        if method_data[2] == "3D":
            maxwell_bcs_dir['boundary_Maxwell_Dir'].append({"name":bc, "value":"{0,0}"})
        else:
            maxwell_bcs_dir['boundary_Maxwell_Dir'].append({"name":bc, "value":"0"})

    for bc in boundary_electric:
        electric_bcs_dir['boundary_Electric_Dir'].append({"name":bc[0], "value":bc[2]})
        

    if method_data[3] == "thelec":
        th_ = Merge(thermic_bcs_rob, thermic_bcs_neu)
        if method_data[2] == "Axi":
            return th_
        else:
            elec_ = Merge(electric_bcs_dir, electric_bcs_neu)
            return Merge(th_, elec_)
    elif method_data[3] == 'mag':
        return maxwell_bcs_dir
    elif method_data[3] == 'thmag':
        th_ = Merge(thermic_bcs_rob, thermic_bcs_neu)
        if method_data[2] == "Axi":
            return Merge(maxwell_bcs_dir, th_)
        else:
            elec_ = Merge(electric_bcs_dir, electric_bcs_neu)
            thelec_ = Merge(th_, elec_)
            return Merge(maxwell_bcs_dir, thelec_)
    else:
        th_ = Merge(thermic_bcs_rob, thermic_bcs_neu)
        elec_ = Merge(electric_bcs_dir, electric_bcs_neu)
        thelec_ = Merge(th_, elec_)
        thelecmeca_ = Merge(thelec_, meca_bcs_dir)
        return Merge(maxwell_bcs_dir, thelecmeca_)
            
    return {}

def create_json(jsonfile: str, mdict: dict, mmat: dict, mpost: dict, templates: dict, method_data: List[str], debug: bool = False):
    """
    Create a json model file
    """

    if debug: print("create_json=", jsonfile)
    print("create_json=", jsonfile)
    print("create_json=", mdict)
    data = entry(templates["model"], mdict, debug)   
    print("create_json/data:", data)
    
    # material section
    if "Materials" in data:
        for key in mmat:
            data["Materials"][key] = mmat[key]
    else:
        data["Materials"] = mmat
    print("create_json/Materials data:", data)

    # postprocess
    if debug: print("flux")
    if "flux" in mpost:
        flux_data = mpost["flux"]
        add = data["PostProcess"]["heat"]["Measures"]["Statistics"]
        odata = entry(templates["flux"], flux_data, debug)
        for md in odata["Flux"]:
            data["PostProcess"]["heat"]["Measures"]["Statistics"][md] = odata["Flux"][md]
    
    if debug: print("meanT_H")
    meanT_data = mpost["meanT_H"] # { "meanT_H": [] }
    add = data["PostProcess"]["heat"]["Measures"]["Statistics"]
    odata = entry(templates["stats"][0], meanT_data, debug)
    for md in odata["Stats_T"]:
        data["PostProcess"]["heat"]["Measures"]["Statistics"][md] = odata["Stats_T"][md]

    if debug: print("current_H")
    section = "electric"
    if method_data[0] == "cfpdes" and method_data[2] == "Axi": section = "heat" 
    currentH_data = mpost["current_H"] # { "Power_H": [] }
    print("currentH_data:", currentH_data)
    print("templates[stats]:", templates["stats"])
    add = data["PostProcess"][section]["Measures"]["Statistics"]
    odata = entry(templates["stats"][2], currentH_data, debug)
    for md in odata["Stats_Current"]:
        data["PostProcess"][section]["Measures"]["Statistics"][md] = odata["Stats_Current"][md]
    
    if debug: print("power_H")
    if method_data[0] == "cfpdes" and method_data[2] == "Axi": section = "heat" 
    powerH_data = mpost["power_H"] # { "Power_H": [] }
    add = data["PostProcess"][section]["Measures"]["Statistics"]
    odata = entry(templates["stats"][1], powerH_data, debug)
    for md in odata["Stats_Power"]:
        data["PostProcess"][section]["Measures"]["Statistics"][md] = odata["Stats_Power"][md]
    
    print("with currents:", data["PostProcess"][section]["Measures"]["Statistics"])

    mdata = json.dumps(data, indent = 4)

    # print("corrected data:", re.sub(r'},\n					    	}\n', '}\n}\n', data))
    # data = re.sub(r'},\n					    	}\n', '}\n}\n', data)
    with open(jsonfile, "x") as out:
        out.write(mdata)
    pass

def entry(template: str, rdata: dict, debug: bool = False) -> str:
    import chevron
    import re
    
    if debug:
        print("entry/loading %s" % str(template), type(template))
        print("entry/rdata:", rdata)
    with open(template, "r") as f:
        jsonfile = chevron.render(f, rdata)
    jsonfile = jsonfile.replace("\'", "\"")
    if debug:
        print("entry/jsonfile:", jsonfile)
        print("corrected:", re.sub(r'},\n[\t ]+}\n', '}\n}\n', jsonfile))

    corrected = re.sub(r'},\n[\t ]+}\n', '}\n}\n', jsonfile)
    corrected = corrected.replace("&quot;", "\"")
    try:
        mdata = json.loads(corrected)
    except json.decoder.JSONDecodeError:
        print("entry: json.decoder.JSONDecodeError")
        print("entry:", corrected)
        sys.exit(1)

    if debug:
        print("entry/data (json):\n", mdata)
   
    return mdata