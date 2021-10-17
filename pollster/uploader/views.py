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


def Concordance(a, bh):
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


def Concordance2(bh, a):
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


def DiscordanceCritere(a, bh, critere):
    ga = Performances[a][critere]
    gbh, qbh, pbh, vbh = Seuils[bh][critere]
    if ga <= gbh - pbh:
        return 0.0
    elif ga > gbh + vbh:
        return 1.0
    else:
        return ((gbh + pbh) - ga) / (pbh + vbh)


def DiscordanceCritere2(bh, a, critere):
    ga = Performances[a][critere]
    gbh, qbh, pbh, vbh = Seuils[bh][critere]
    if gbh <= ga - 0:
        return 0.0
    elif gbh > ga + 0:
        return 1.0


def crédibilité(a, bh):
    mult = 1
    for critere in Criteres:
        mult = mult * ((2 - DiscordanceCritere(a, bh, critere)) / (2 - Concordance(a, bh)))
    sigma_abh = Concordance(a, bh) * mult
    return sigma_abh


def crédibilité2(bh, a):
    mult = 1
    for critere in Criteres:
        mult = mult * ((2 - DiscordanceCritere2(bh, a, critere)) / (2 - Concordance2(bh, a)))
    sigma_abh = Concordance2(bh, a) * mult
    return sigma_abh


def electretri():
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
            if crédibilité(a, classe) >= Lambda and crédibilité2(classe, a) >= Lambda:
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

            elif crédibilité(a, classe) >= Lambda and crédibilité2(classe, a) < Lambda:
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
            elif crédibilité(a, classe) < Lambda and crédibilité2(classe, a) >= Lambda:
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
            elif crédibilité(a, classe) < Lambda and crédibilité2(classe, a) < Lambda:

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


def launchElectre(request,id):
    file=Upload.objects.get(pk=id)
    df = pd.read_excel(file.pic.file)
    number_of_lines = df.shape[0]
    number_of_cols = df.shape[1]

    actions = []
    for i in range(1, number_of_lines):
        if search("PDV", str(list(df.iloc[i])[0])):
            actions.append(list(df.iloc[i])[0])


    actions.sort()
    print(actions)
    classe1 = random.choice(actions,3)
    classe2 = random.choice(actions,3)
    classe3 = random.choice(actions,3)
    classe4 = random.choice(actions,3)
    classe5 = random.choice(actions,3)

    return render(request,'electre.html',
        {
            "actions":actions,
            "classe1":classe1, 
            "classe2":classe2, 
            "classe3":classe3, 
            "classe4":classe4, 
            "classe5":classe5 
        })
    
