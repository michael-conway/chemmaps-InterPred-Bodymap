from os import system, path
from .toolbox import loadMatrixToDict, loadMatrixInfoToDict, convertSMILEStoINCHIKEY, loadMap1D2D3D
from .DBrequest import DBrequest
from .uploadMap import loadingMap

import math
from copy import deepcopy


# to format desc for map
# DrugMap
DDESCDRUGMAP = {"JCHEM_ROTATABLE_BOND_COUNT":"Rotable bond", "JCHEM_POLAR_SURFACE_AREA": "Polar surface",
               "MOLECULAR_WEIGHT": "Molecular weight", "JCHEM_PHYSIOLOGICAL_CHARGE": "Physio charge",
               "JCHEM_RULE_OF_FIVE": "Rule of five", "JCHEM_VEBER_RULE": "Veber rule", "FORMULA": "Formula",
               "JCHEM_GHOSE_FILTER": "Ghose filter","GENERIC_NAME": "Generic name",
               "JCHEM_TRADITIONAL_IUPAC":"IUPAC", "ALOGPS_SOLUBILITY": "Solubility",
               "JCHEM_MDDR_LIKE_RULE": "MDDR rule", "PRODUCTS": "Product",
               "ALOGPS_LOGP": "ALogP", "JCHEM_PKA_STRONGEST_BASIC": "Pka Basic",
               "JCHEM_NUMBER_OF_RINGS": "Number of rings", "JCHEM_PKA": "PKA",
               "JCHEM_ACCEPTOR_COUNT": "Acceptor count", "JCHEM_PKA_STRONGEST_ACIDIC": "Pka acidic",
               "EXACT_MASS": "Exact mass", "JCHEM_DONOR_COUNT": "Donor count", "INTERNATIONAL_BRANDS": "Brands",
               "JCHEM_AVERAGE_POLARIZABILITY": "Polarizability","JCHEM_BIOAVAILABILITY": "Bioavailability",
               "DATABASE_NAME": "Database", "JCHEM_REFRACTIVITY": "Refractivity", "JCHEM_LOGP": "LogP",
               "JCHEM_FORMAL_CHARGE": "Formal charge", "SALTS": "Salt", "JCHEM_ATOM_COUNT": "Atom count", "SMILES":"SMILES"}

DDESCDSSTOX = {"EPA_category": "EPA category", "LD50_mgkg": "LD50 (mg/kg)",
               "CATMoS_VT_pred": "Acute Tox (very toxic)", "CATMoS_NT_pred": "Acute Tox (no toxic)",
               "CATMoS_EPA_pred": "Acute Tox (EPA)", "CATMoS_GHS_pred": "Acute Tox (GHS)",
               "CATMoS_LD50_pred": "Acute Tox (LD50)", "CERAPP_Ago_pred": "Estrogen Receptor activity (Agonist)",
               "CERAPP_Bind_pred": "Estrogen Receptor activity (binding)", "Clint_pred": "Hepatic clearance",
               "CoMPARA_Anta_pred": "Androgen Receptor Activity (Antogonist)",
               "CoMPARA_Bind_pred": "Androgen Receptor Activity (binding)",
               "FUB_pred": "Plasma fraction unbound", "LogHL_pred": "Henry’s Law constant (atm-mol3/mole)",
               "LogKM_pred": "KM (biotransformation rate)", "LogKOA_pred": "Log Octanol/air partition coefficient",
               "LogKoc_pred": "Log Soil adsorption coefficient (L/Kg)",
               "LogBCF_pred": "Log Fish bioconcentration factor",
               "LogD55_pred": "LogD", "LogP_pred": "LogP", "MP_pred": "Melting Point (C)", "pKa_a_pred": "Pka acid",
               "pKa_b_pred": "Pka basic", "ReadyBiodeg_pred": "Biodegradability", "RT_pred": "HPLC retention time",
               "LogVP_pred": "Log vapor pressure (mmHg)", "LogWS_pred": "Log Water solubility", "MolWeight": "MW",
               "LogOH_pred": "Log Atmospheric constant (cm3/molsec)",
               "BioDeg_LogHalfLife_pred": "Biodegradation half-life",
               "BP_pred": "Boiling Point", "nbLipinskiFailures": "Lipinski Failures"}



class JSbuilder:

    def __init__(self, nameMap, prout = ""):
        self.nameMap = nameMap
        self.prout = prout
        self.pMap = path.abspath("./static/chemmaps/map/" + self.nameMap) + "/"
        self.err = 0


    def loadMap(self, ldescMap = [], IDmap = 1):

        self.ldescMap = ldescMap# prop in
        #cDB = DBrequest()
        if self.nameMap == "DrugMap":
            cload = loadingMap(self.nameMap, self.ldescMap)
            dmap = cload.loadMap()
        elif self.nameMap == "PFASMap" or self.nameMap == "Tox21Map":
            dmap = {}
            dmap["coord"] = loadMap1D2D3D(self.pMap)
            # modif with user choose
            dmap["info"] = loadMatrixInfoToDict(self.pMap + "TableProp.csv", sep = "\t", ldesc=ldescMap)
            dmap["neighbor"] = loadMatrixToDict(self.pMap + "TableNeighbors.csv")

        elif self.nameMap == "DSSToxMap":
            self.IDmap = IDmap
            dmap = {}
            dmap["coord"] = loadMap1D2D3D(self.pMap + str(IDmap))
            # modif with user choose
            dmap["info"] = loadMatrixInfoToDict(self.pMap + str(IDmap) + "_TableProp.csv", sep="\t", ldesc=ldescMap)
            dmap["neighbor"] = loadMatrixToDict(self.pMap + str(IDmap) + "_TableNeighbors.csv")
        self.map = dmap



    def generateJS(self):

        dout = {}

        ###############
        # coordinates #
        ###############

        #map
        dcoord = {}
        for IDchem in self.map["coord"].keys():
            dcoord[IDchem] = [float(self.map["coord"][IDchem]["DIM1"]), float(self.map["coord"][IDchem]["DIM2"]), float(self.map["coord"][IDchem]["DIM3"])]
        # user chem
        if "dchemAdd" in self.__dict__:
            for IDadd in self.dchemAdd["coord"].keys():
                dcoord[IDadd] = [float(self.dchemAdd["coord"][IDadd]["DIM1"]), float(self.dchemAdd["coord"][IDadd]["DIM2"]), float(self.dchemAdd["coord"][IDadd]["DIM3"])]

        ########
        # Info #
        ########
        if self.nameMap == "DrugMap":
            # to formate on map
            dinfo = {}
            for IDchem in self.map["info"].keys():
                dinfo[IDchem] = {}

                for k in self.map["info"][IDchem].keys():
                    dinfo[IDchem][DDESCDRUGMAP[k]] = self.map["info"][IDchem][k]

            # user chem
            if "dchemAdd" in self.__dict__:
                for IDadd in self.dchemAdd["info"].keys():
                    dinfo[IDadd] = {}
                    for k in self.dchemAdd["info"][IDadd].keys():
                        dinfo[IDadd][DDESCDRUGMAP[k]] = self.dchemAdd["info"][IDadd][k]


        if self.nameMap == "DSSToxMap" or self.nameMap == "PFASMap" or self.nameMap == "Tox21Map":
            # to formate to map
            dinfo = {}
            #map
            for IDchem in self.map["info"].keys():
                dinfo[IDchem] = {}
                for k in self.map["info"][IDchem].keys():
                    dinfo[IDchem][DDESCDSSTOX[k]] = self.map["info"][IDchem][k]

            # add chem
            if "dchemAdd" in self.__dict__:
                for IDadd in self.dchemAdd["info"].keys():
                    dinfo[IDadd] = {}
                    for k in self.dchemAdd["info"][IDadd].keys():
                        dinfo[IDadd][DDESCDSSTOX[k]] = self.dchemAdd["info"][IDadd][k]




        #############
        # Neighbors #
        #############

        dneighbor = {}
        # map transform inchikey to DBID
        for IDchem in self.map["neighbor"].keys():
            dneighbor[IDchem] = []
            for neighbor in self.map["neighbor"][IDchem]:
                try:dneighbor[IDchem] = dneighbor[IDchem] + self.map["inchikey"][neighbor]
                except: pass

        # user chem
        if "dchemAdd" in self.__dict__:
            for IDadd in self.dchemAdd["neighbor"].keys():
                dneighbor[IDadd] = self.dchemAdd["neighbor"][IDadd]



        ####################
        # SMILES and Class #
        ####################

        if self.nameMap == "DrugMap":
            dSMILES = self.map["SMILESClass"]
            # using file
            #dSMILES = loadMatrixInfoToDict(self.pMap + "TableProp.csv", sep="\t", ldesc=["SMILES", "DRUG_GROUPS", "inchikey"])

        if self.nameMap == "DSSToxMap" or self.nameMap == "PFASMap" or self.nameMap == "Tox21Map":
            try: dSMILES = loadMatrixInfoToDict(self.pMap + str(self.IDmap) + "_TableProp.csv", sep="\t", ldesc=["SMILES", "GHS_category", "inchikey"])
            except: dSMILES = loadMatrixInfoToDict(self.pMap + "TableProp.csv", sep="\t", ldesc=["SMILES", "GHS_category", "inchikey"])

        if "dchemAdd" in self.__dict__:
            for IDadd in self.dchemAdd["SMILESClass"].keys():
                dSMILES[IDadd] = {}
                dSMILES[IDadd] = deepcopy(self.dchemAdd["SMILESClass"][IDadd])


                # add smiles for added chemicals
        dout["coord"] = dcoord
        dout["info"] = dinfo
        dout["neighbor"] = dneighbor
        dout["SMILESClass"] = dSMILES

        return dout


    ###################
    # MANAGE ADD file #
    ###################

    def generateCoords(self, p1D2D, p3D):

        self.inDB = 0
        # define the all structure here of output
        if not "dchemAdd" in self.__dict__:
            self.dchemAdd = {}
            self.dchemAdd["p2D"] = p1D2D
            self.dchemAdd["p3D"] = p3D
            self.dchemAdd["coord"] = {}
            self.dchemAdd["info"] = {}
            self.dchemAdd["SMILESClass"] = {}
            self.dchemAdd["neighbor"] = {}

        # control if included in DB
        filin = open(p1D2D, "r")
        llines = filin.readlines()
        filin.close()
        ldesc = llines[0].strip().split("\t")
        i = 1
        imax = len(llines)
        while i < imax:
            lval = llines[i].strip().split("\t")
            inchikey = lval[2]
            id = lval[0]
            smiles = lval[1]

            ddesc = {}
            d = 0
            dmax = len(ldesc)
            while d < dmax:
                ddesc[ldesc[d]] = lval[d]
                d = d + 1

            dcoord = downloadCoordsFromDB(self.nameMap, inchikey, "3D")
            # manage coord
            if dcoord != [] and dcoord != "Error":
                self.dchemAdd["coord"][id] = {}
                self.dchemAdd["coord"][id]["DIM1"] = dcoord[0]
                self.dchemAdd["coord"][id]["DIM2"] = dcoord[1]
                self.dchemAdd["coord"][id]["DIM3"] = dcoord[2]


                # take info and neighbor
                dinfo = downloadInfoFromDB(self.nameMap, inchikey)
                lneighbor = downloadNeighborsFromDB(self.nameMap, inchikey)
                
                #info
                self.dchemAdd["info"][id] = {}
                self.dchemAdd["SMILESClass"][id]= {}
                self.dchemAdd["SMILESClass"][id]["SMILES"] = smiles
                self.dchemAdd["SMILESClass"][id]["inchikey"] = inchikey

                if self.nameMap == "DrugMap":
                    self.dchemAdd["SMILESClass"][id]["DRUG_GROUPS"] = "add"
                else:
                    self.dchemAdd["SMILESClass"][id]["GHS_category"] = "add"


                for desc in self.ldescMap:
                    if desc in list(ddesc.keys()):
                        self.dchemAdd["info"][id][desc] = ddesc[desc]
                    elif desc in list(dinfo.keys()):
                        self.dchemAdd["info"][id][desc] = dinfo[desc]
                    else:
                        self.dchemAdd["info"][id][desc] = "NA"
                
                # neighbor
                if lneighbor != [] and lneighbor != "Error":
                    self.dchemAdd["neighbor"] = lneighbor

                del llines[i]
                imax = imax - 1
                continue
            
            else:
                i = i + 1 

        if len(llines) == 1:
            self.inDB = 1
            return 
        
        #filout = open(p1D2D, "w")
        #filout.write("".join(llines))
        #filout.close()
            
        cmd = "%s/addonMap.R %s %s %s1D2Dscaling.csv %s3Dscaling.csv %sCP1D2D.csv %sCP3D.csv %s"%(path.abspath("./chemmaps/Rscripts"), p1D2D, p3D, self.pMap, self.pMap, self.pMap, self.pMap, self.prout)
        print(cmd)
        system(cmd)

        p1D2Dcoord = self.prout + "coord1D2D.csv"
        p3Dcoord = self.prout + "coord3D.csv"


        if path.exists(p1D2Dcoord) and path.exists(p3Dcoord):
            self.dchemAdd["coord"].update(loadMap1D2D3D(self.prout))
        
        if self.dchemAdd["coord"] == {}:
            self.err = 1
            return "ERROR"



    def findneighbor(self, nbneighbor=20):


        if self.err == 1:
            return "ERROR"

        if not "dchemAdd" in self.__dict__:
            print("ERROR -> generate first coordinate")
            self.err = 1
            return "ERROR"

        self.dchemAdd["neighbor"] = {}

        for ID in self.dchemAdd["coord"].keys():
            x = self.dchemAdd["coord"][ID]["DIM1"]
            y = self.dchemAdd["coord"][ID]["DIM2"]
            z = self.dchemAdd["coord"][ID]["DIM3"]

            dcor1 = [float(x), float(y), float(z)]
            ddist = {}
            ddist[ID] = {}

            for ID2 in self.map["coord"].keys():
                x2 = self.map["coord"][ID2]["DIM1"]
                y2 = self.map["coord"][ID2]["DIM2"]
                z2 = self.map["coord"][ID2]["DIM3"]

                dcor2 = [float(x2), float(y2), float(z2)]
                ddist[ID][ID2] = math.sqrt(sum([(xi - yi) ** 2 for xi, yi in zip(dcor1, dcor2)]))

            lID = [i[0] for i in sorted(ddist[ID].items(), key=lambda x: x[1])][:nbneighbor]

            self.dchemAdd["neighbor"][ID] = lID



    def findinfoTable(self):

        if not "dchemAdd" in self.__dict__:
            print("ERROR -> generate first coordinate")
            return "ERROR"


        if self.inDB == 1:
            return
        

        # load Desc 2D
        d2Ddesc = loadMatrixInfoToDict(self.dchemAdd["p2D"])

        for IDadd in d2Ddesc.keys():
            if str(IDadd) in list(self.dchemAdd["info"].keys()):
                print("ddddddd")
                continue
            else:
                self.dchemAdd["info"][IDadd] = {}
                self.dchemAdd["SMILESClass"][IDadd] = {}

                #SMILES
                self.dchemAdd["SMILESClass"][IDadd]["SMILES"] = d2Ddesc[IDadd]["SMILES"]


                if self.nameMap == "DrugMap":
                    self.dchemAdd["SMILESClass"][IDadd]["DRUG_GROUPS"] = "add"
                    self.dchemAdd["SMILESClass"][IDadd]["inchikey"] = convertSMILEStoINCHIKEY(d2Ddesc[IDadd]["SMILES"])
                else:
                    self.dchemAdd["SMILESClass"][IDadd]["GHS_category"] = "add"
                    self.dchemAdd["SMILESClass"][IDadd]["inchikey"] = convertSMILEStoINCHIKEY(d2Ddesc[IDadd]["SMILES"])

                # info
                for desc in self.ldescMap:
                    if desc in list(d2Ddesc[IDadd].keys()):
                        self.dchemAdd["info"][IDadd][desc] = d2Ddesc[IDadd][desc]
                    else:
                        self.dchemAdd["info"][IDadd][desc] = "NA"


def downloadCoordsFromDB(map, inchikey, typeCoord):

    cDB = DBrequest()
    cDB.verbose = 0

    if map == "DrugMap":
        table = "drugbank_coords"

    lval = cDB.getRow(table, "inchikey='%s'"%(inchikey))
    #print(lval[0][0])
    if lval == "Error" and lval == []:
        return []

    if typeCoord == "3D":
        lout = [lval[0][1][0], lval[0][1][1], lval[0][2][0]]
    
    return lout


def downloadInfoFromDB(map, inchikey):
    cDB = DBrequest()
    cDB.verbose = 0

    if map == "DrugMap":
        table_chem = "drugbank_chem"
        table_prop = "drugbank_prop"
        table_prop_name = "drugbank_name_prop"
    
    # find name chem in DB
    dbID = cDB.extractColoumn(table_chem, "db_id", "WHERE inchikey='%s'"%(inchikey))
    if dbID == [] or  dbID == "Error":
        return {}
    else :
        dbID = dbID[0][0]
        lval = cDB.extractColoumn(table_prop, "prop_value", "WHERE db_id='%s'"%(dbID))
        lval = lval[0][0]
        lprop =  cDB.extractColoumn(table_prop_name, "name")
        lprop = [prop [0] for prop in lprop]
        
        dout = {}
        i = 0
        imax = len(lprop)
        while i < imax:
            dout[lprop[i]] = lval[i]
            i = i + 1

        return dout

def downloadNeighborsFromDB(map, inchikey):

    cDB = DBrequest()
    cDB.verbose = 0

    if map == "DrugMap":
        table_neighbors = "drugbank_neighbors"

    lneighbor  =  cDB.extractColoumn(table_neighbors, "neighbors_dim3")
    if lneighbor == "Error" or lneighbor == []:
        return []
    else:
        return lneighbor[0]
