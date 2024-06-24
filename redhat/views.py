from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from openpyxl.reader.excel import load_workbook
from pymongo import MongoClient

client = MongoClient()

import random

import pandas as pd

import calendar

import datetime as dt

from pymongo import MongoClient

def montecarlo(request):
    return render(request, 'redhat/montecarlo.html')



class MontecarloExecute(APIView):
    def post(self, request, *args, **kwargs):
        issuetype = request.data.get('issuetype')
        resolutiondate = request.data.get('resolutiondate')
        print(issuetype)
        print(resolutiondate)

        # Provide the connection details
        hostname = 'localhost'
        port = 27017  # Default MongoDB port
        # Create a MongoClient instance
        client = MongoClient(hostname, port)

        db = client['JiraRepos']
        mongo_collection = db['RedHat']

        # x = mongo_collection.find_one({"fields.issuetype.name": "Bug"})

        x = mongo_collection.find(
            {"$and": [{"fields.issuetype.name": issuetype}, {"fields.resolutiondate": {"$ne": None}}]})

        dateslist = []
        for issue in x:
            dateslist.append(issue["fields"]["resolutiondate"])

        client.close()

        dict = {"resolutiondate": dateslist}

        df = pd.DataFrame(dict)

        df = df.sort_values(by="resolutiondate")

        df['resolutiondate'] = pd.to_datetime(df['resolutiondate'], dayfirst=False)

        df1 = df['resolutiondate'].dt.date.value_counts().sort_index().reset_index()
        df1.columns = ['DATE', 'Count']

        # df1.to_excel("enhancement_data_filtered.xlsx")

        class MonthData:
            def __init__(self, days, counts):
                self.days = days
                self.counts = counts

        # Montecarlo

        class Simulation:
            def __init__(self, simulated_throughtput, count):
                self.simulated_throughtput = simulated_throughtput
                self.count = count
        month_forecast_target = resolutiondate

        year_historic_target = 2016

        max_rng = calendar._monthlen(year_historic_target, month_forecast_target)

        df1['DATE'] = pd.to_datetime(df1.DATE, format='%Y-%m-%d')

        filtered_df = df1[df1['DATE'].dt.year == year_historic_target]

        filtered_df = filtered_df[filtered_df['DATE'].dt.month == month_forecast_target]

        throughput_days = []

        throughput_counts = []

        for x in range(1, max_rng + 1):
            throughput_days.append(x)
            throughput_counts.append(0)

        # Completamos el objeto para simular

        for index, row in filtered_df.iterrows():
            throughput_counts[row["DATE"].day - 1] = row["Count"]


        montecarlo_target = 1000

        list_of_simulations = []

        # Bucle generativo

        for x in range(1, montecarlo_target + 1):
            simulated_throughtput = 0
            for day in throughput_days:
                rng_tmp = random.randint(1, max_rng)
                simulated_throughtput = simulated_throughtput + throughput_counts[rng_tmp - 1]

            aux = 0
            found = False

            for simulation in list_of_simulations:
                if simulation.simulated_throughtput == simulated_throughtput:
                    tmp_simulation = simulation
                    tmp_simulation.count = tmp_simulation.count + 1
                    list_of_simulations[aux] = tmp_simulation
                    found = True
                    break
                aux = aux + 1
            if not found:
                list_of_simulations.append(Simulation(simulated_throughtput, 1))

        print(throughput_counts)
        print(throughput_days)

        montecarlo_output = pd.DataFrame([t.__dict__ for t in list_of_simulations])

        montecarlo_output_sorted = montecarlo_output.sort_values(by='simulated_throughtput')

        data_throughtput = {'days': throughput_days, 'counts': throughput_counts}
        df_throughtput = pd.DataFrame(data_throughtput)

        montecarlo_output_json = montecarlo_output_sorted.to_json(orient='records')
        df_throughput_json = df_throughtput.to_json(orient='records')

        return Response({
            'montecarlo_output': montecarlo_output_json,
            'df_throughput': df_throughput_json
        }, status=status.HTTP_200_OK)
