from django.shortcuts import render
from uploader.models import UploadForm,Upload
from django.http import HttpResponseRedirect
from django.urls import reverse
from pandas import DataFrame, read_csv
import random
from numpy import random

from django.http import JsonResponse
import pandas as pd
from re import search


# Create your views here.
def home(request):
    if request.method=="POST":
        img = UploadForm(request.POST, request.FILES)       
        if img.is_valid():
            img.save()  
            return HttpResponseRedirect(reverse('imageupload'))
    else:
        img=UploadForm()
    files=Upload.objects.all().order_by('-upload_date')
    return render(request,'home.html',{'form':img,'files':files})


def showFile(request, id): 
    file=Upload.objects.get(pk=id)
    #try to dispaly file in html table
    df = pd.read_excel(file.pic.file)
    data=   df.to_json(orient='split')
    return render(request,'acp.html',{'file':file,'data':data})


def Concordance(a, bh,Criteres,Poids,Performances,Seuils):
    conc = 0.0
    for critere in Criteres:
        poids = Poids[critere]
        ga = Performances[a][critere]
        gbh, qbh, pbh, vbh = Seuils[bh][critere]
        if gbh - ga >= pbh:
            conc += 0.0 * poids
        elif gbh - ga <= qbh:
            conc += 1.0 * poids
        else:
            conc += ((pbh + ga - gbh) / (pbh - qbh)) * poids
    return conc


def Concordance2(bh, a,Criteres,Poids,Performances,Seuils):
    conc = 0.0
    for critere in Criteres:
        poids = Poids[critere]
        ga = Performances[a][critere]
        gbh, qbh, pbh, vbh = Seuils[bh][critere]
        if ga - gbh >= 0:
            conc += 0.0 * poids
        elif ga - gbh <= 0:
            conc += 1.0 * poids
    return conc


def DiscordanceCritere(a, bh, critere,Performances,Seuils):
    ga = Performances[a][critere]
    gbh, qbh, pbh, vbh = Seuils[bh][critere]
    if ga <= gbh - pbh:
        return 0.0
    elif ga > gbh + vbh:
        return 1.0
    else:
        return ((gbh + pbh) - ga) / (pbh + vbh)


def DiscordanceCritere2(bh, a, critere,Performances,Seuils):
    ga = Performances[a][critere]
    gbh, qbh, pbh, vbh = Seuils[bh][critere]
    if gbh <= ga - 0:
        return 0.0
    elif gbh > ga + 0:
        return 1.0


def crédibilité(a, bh,Criteres,Performances,Seuils,Poids):
    mult = 1
    for critere in Criteres:
        mult = mult * ((2 - DiscordanceCritere(a, bh, critere,Performances,Seuils)) / (2 - Concordance(a, bh,Criteres,Poids,Performances,Seuils)))
    sigma_abh = Concordance(a, bh,Criteres,Poids,Performances,Seuils) * mult
    return sigma_abh


def crédibilité2(bh, a,Criteres,Performances,Seuils,Poids):
    mult = 1
    for critere in Criteres:
        mult = mult * ((2 - DiscordanceCritere2(bh, a, critere,Performances,Seuils)) / (2 - Concordance2(bh, a,Criteres,Poids,Performances,Seuils)))
    sigma_abh = Concordance2(bh, a,Criteres,Poids,Performances,Seuils) * mult
    return sigma_abh


def electretri(Actions,Classes,Criteres,Performances,Seuils,Poids,Lambda):
    PE = []
    PD = []
    PC = []
    PB = []
    PA = []
    OE = []
    OD = []
    OC = []
    OB = []
    OA = []
    for a in Actions:
        i = 0
        z = 0
        l = 0
        p = 0
        # ['A', 'B', 'C', 'd', 'E']
        for classe in Classes[:-1]:
            if crédibilité(a, classe,Criteres,Performances,Seuils,Poids) >= Lambda and crédibilité2(classe, a,Criteres,Performances,Seuils,Poids) >= Lambda:
                l = l + 1
                if classe == 'E' and i == 0:
                    PD.append(a)
                    l = l + 1
                    i = 1
                if classe == 'D' and i == 0:
                    PC.append(a)
                    l = l + 1
                    i = 1
                if classe == 'C' and i == 0:
                    PB.append(a)
                    l = l + 1
                    i = 1
                if classe == 'B' and i == 0:
                    PA.append(a)
                    l = l + 1
                    i = 1
                if classe == 'E' and z == 0:
                    OE.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'D' and z == 0:
                    OD.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'C' and z == 0:
                    OC.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'B' and z == 0:
                    OB.append(a)
                    z = z + 1
                    l = l + 1
                if l == 5 and i == 1 and z == 0:
                    OA.append(a)
                if l == 5 and i == 0 and z == 1:
                    PE.append(a)

            elif crédibilité(a, classe,Criteres,Performances,Seuils,Poids) >= Lambda and crédibilité2(classe, a,Criteres,Performances,Seuils,Poids) < Lambda:
                l = l + 1
                if classe == 'E' and i == 0:
                    PD.append(a)
                    i = i + 1
                    l = l + 1
                if classe == 'D' and i == 0:
                    PC.append(a)
                    i = i + 1
                    l = l + 1
                if classe == 'C' and i == 0:
                    PB.append(a)
                    i = i + 1
                    l = l + 1
                if classe == 'B' and i == 0:
                    PA.append(a)
                    i = i + 1
                    l = l + 1
                if l == 5:
                    OA.append(a)
            elif crédibilité(a, classe,Criteres,Performances,Seuils,Poids) < Lambda and crédibilité2(classe, a,Criteres,Performances,Seuils,Poids) >= Lambda:
                l = l + 1
                if classe == 'E' and z == 0:
                    OE.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'D' and z == 0:
                    OD.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'C' and z == 0:
                    OC.append(a)
                    z = z + 1
                    l = l + 1
                if classe == 'B' and z == 0:
                    OB.append(a)
                    z = z + 1
                    l = l + 1
                if l == 5:
                    PE.append(a)
            elif crédibilité(a, classe,Criteres,Performances,Seuils,Poids) < Lambda and crédibilité2(classe, a,Criteres,Performances,Seuils,Poids) < Lambda:

                if (i == 0 and z == 0) or (z == 1 and i == 1) and p == 0:
                    OA.append(a)
                    PE.append(a)
                    z = z + 1
                    i = i + 1
                    p = p + 1
                if i == 1 and z == 0 and p == 0:
                    OA.append(a)
                    z = z + 1
                if i == 0 and z == 1 and p == 0:
                    PE.append(a)
                    i = i + 1

    resulta = [PE, PD, PC, PB, PA, OE, OD, OC, OB, OA]
    return resulta
    

def launchElectre(request,id):
    file=Upload.objects.get(pk=id)
    df = pd.read_excel(file.pic.file)
    Classes = ['E', 'D', 'C', 'B', 'A']

    lenclasses = len(Classes)
    minus = lenclasses+3
    dimensions = df.shape
    x=dimensions[0]

    Poids=(df.iloc[-1]).to_dict()
    Poids.pop('Alternative')

    Criteres = list(Poids.keys())

    first_column = (df.iloc[:, 0]).to_dict()
    values = first_column.values()
    values_list = list(values)
    Actions = []
    for i in range(0,dimensions[0]-minus):
        Actions.append(values_list[i])

    per = (df.iloc[:dimensions[0]-minus, 1:]).to_dict('records')

    Performances = {}
    for i in range(0,len(Actions)):
        Performances[Actions[i]] = per[i]

    seu = (df.iloc[dimensions[0]-minus:dimensions[0]-1, 1:]).to_dict('split')
    p = lenclasses - 1
    q = lenclasses
    v = lenclasses + 1
    Seuils = {}
    for n in range(0,minus-4):
        t = {}
        for m in range(0,minus-3):
            t[seu['columns'][m]] = [seu['data'][n][m],seu['data'][p][m],seu['data'][q][m],seu['data'][v][m]]
        Seuils[Classes[n]] = t

    Lambda = 0.75

    for classe in Classes[:-1]:
        resulta = electretri(Actions,Classes,Criteres,Performances,Seuils,Poids,Lambda)

    print('\n\n****************optimiste******************')
    print('\n', resulta[0], 'E\n', resulta[1], 'D\n', resulta[2], 'C\n', resulta[3], 'B\n', resulta[4], 'A\n')
    print('****************optimiste******************\n\n\n\n\n')
    print('****************pessimiste******************')
    print('\n', resulta[5], 'E\n', resulta[6], 'D\n', resulta[7], 'C\n', resulta[8], 'B\n', resulta[9], 'A\n')
    print('****************pessimiste******************')


    return render(request,'electre.html',
        {
            "resulta":resulta,
            "resulta0":resulta[0],
            "resulta1":resulta[1],
            "resulta2":resulta[2],
            "resulta3":resulta[3],
            "resulta4":resulta[4],
            "resulta5":resulta[5],
            "resulta6":resulta[6],
            "resulta7":resulta[7],
            "resulta8":resulta[8],
            "resulta9":resulta[9]
            
        })
    
