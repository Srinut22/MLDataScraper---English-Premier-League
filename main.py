import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
team_and_keys = {"Tottenham-Hotspur":["361ca564", 0], "Manchester-City":["b8fd03ef",1], "Liverpool":["822bd0ba",2], "Arsenal": ["18bb7c10",3], "Aston-Villa":["8602292d",4]
                 , "Newcastle-United":["b2b47a98",5], "Brighton-and-Hove-Albion":["d07537b9",6], "Manchester-United":["19538871",7], 
                 "Brentford":["cd051869",8], "Chelsea":["cff3d9bb",9], "Crystal-Palace":["47c64c55",10], "West-Ham-United":["7c21e445",11], 
                 "Nottingham-Forest":["e4a775cb",12], "Wolverhampton-Wanderers":["8cec06e1",13], "Fulham":["fd962109",14], "Everton":["d3fd31cc",15], 
                 "Luton-Town":["e297cd13",16], "Bournemouth":["4ba7cbea",17], "Burnley":["943e8050",18], "Sheffield-United":["1df6b87e",19]}

def getGoalsAndPenalties(goals_for):
        goals = int(goals_for[:goals_for.index('(')])
        penalties = int(goals_for[(goals_for.index('(')+1):goals_for.index(')')])
        return goals, penalties

def convertDate(date):
        string = date.split('-')
        val = 0
        for value in string:
            val = val * 100 + int(value)
        return val

def getVenue(venue):
    if venue == "Home":
        return 2
    elif venue == "Away":
        return 1
    else:
        return 0

def extract_info(parsed_code):
    date_elements = parsed_code.find_all("th", {"data-stat": "date"})
    date_elements = [th_element for th_element in date_elements if th_element.find("a")]
    dates = []
    calculation_dates = []
    
    goals_for_elements = parsed_code.find_all("td", {"data-stat": "goals_for"})
    goals_for_values = []

    goals_against_elements = parsed_code.find_all("td", {"data-stat": "goals_against"})
    goals_against_values = []
    
    opponent_elements = parsed_code.find_all("td", {"data-stat": "opponent"})
    opponents = []
    calculation_opponents = []

    venue_elements = parsed_code.find_all("td", {"data-stat":"venue"})
    venues = []
    calculation_venues = []

    calculation_penalties_for_values = []
    calculation_penalties_against_values = []
    calculation_goals_for_values = []
    calculation_goals_against_values = []

    
    for date_element, goals_for_element, goals_against_element, opponent_element, venue_element in zip(date_elements, goals_for_elements, goals_against_elements, opponent_elements, venue_elements):
        date = date_element.a.get_text() if date_element.a else date_element.get_text()
        goals_for = goals_for_element.get_text()
        goals_against = goals_against_element.get_text()
        opponent = opponent_element.a.get_text() if opponent_element.a else opponent_element.get_text()
        venue = venue_element.get_text()
        calculation_venue = getVenue(venue)
        dates.append(date)
        calculation_date = convertDate(date)
        goals_for_values.append(goals_for)
        goals_against_values.append(goals_against)
        opponents.append(opponent)
        venues.append(venue)


        opponent = opponent.split(' ')
        if opponent[0] == "Nott'ham":
            opponent[0] = "Nottingham"
        elif len(opponent) == 2 and opponent[1] == "Utd":
            opponent[1] = "United"
        temp = ""
        for value in opponent:
            temp = temp + value + "-"
        
        opponent = temp[0:len(temp)-1]
        if opponent in team_and_keys.keys():
            calculation_opponent = team_and_keys[opponent][1]

            if type(goals_for) != int and '(' and ')' in goals_for:
                calculation_goals_for, calculation_penalties_for = getGoalsAndPenalties(goals_for)
            else:
                calculation_goals_for = int(goals_for)
                calculation_penalties_for = 0
        
            if type(goals_against) != int and '(' and ')' in goals_against:
                calculation_goals_against, calculation_penalties_against = getGoalsAndPenalties(goals_against)
            else:
                calculation_goals_against = int(goals_against)
                calculation_penalties_against = 0

            calculation_opponents.append(calculation_opponent)
            calculation_goals_for_values.append(calculation_goals_for)
            calculation_penalties_for_values.append(calculation_penalties_for)
            calculation_goals_against_values.append(calculation_goals_against)
            calculation_penalties_against_values.append(calculation_penalties_against)
            calculation_venues.append(calculation_venue)
            calculation_dates.append(calculation_date)
        else:
            continue
    return dates, goals_for_values, goals_against_values, opponents, venues, calculation_dates, calculation_goals_for_values, calculation_penalties_for_values, calculation_goals_against_values, calculation_penalties_against_values, calculation_opponents, calculation_venues

def getGameHistory(team_name):
    years = [f"{year}-{year + 1}" for year in range(2023, 1995, -1)]

    dates, goals_for, goals_against, opponents, venues = [], [], [], [], []
    calculation_dates, calculation_goals_for, calculation_penalties_for, calculation_goals_against, calculation_penalties_against, calculation_opponents, calculation_venues = [], [], [], [], [], [], []

    for year in years:
        HTML_markup = requests.get(f"https://fbref.com/en/squads/{team_and_keys[team_name][0]}/{year}/{team_name}-Stats").text
        parsed_code = BeautifulSoup(HTML_markup, 'html.parser')
        
        extracted_data = extract_info(parsed_code)
        
        dates.extend(extracted_data[0])
        goals_for.extend(extracted_data[1])
        goals_against.extend(extracted_data[2])
        opponents.extend(extracted_data[3])
        venues.extend(extracted_data[4])
        calculation_dates.extend(extracted_data[5])
        calculation_goals_for.extend(extracted_data[6])
        calculation_penalties_for.extend(extracted_data[7])
        calculation_goals_against.extend(extracted_data[8])
        calculation_penalties_against.extend(extracted_data[9])
        calculation_opponents.extend(extracted_data[10])
        calculation_venues.extend(extracted_data[11])

    # Create DataFrame
    data_dict = {
        "Date": dates,
        "Goals For": goals_for,
        "Goals Against": goals_against,
        "Opponents": opponents,
        "Venue": venues
    }

    calculation_data_dict = {
        "Date": calculation_dates,
        "Goals For": calculation_goals_for,
        "Goals Against": calculation_goals_against,
        "Penalties For":calculation_penalties_for,
        "Penalties Against":calculation_penalties_against,
        "Opponents": calculation_opponents,
        "Venue": calculation_venues
    }

    calculation_match_data = pd.DataFrame(calculation_data_dict)
    finished_match_data = pd.DataFrame(data_dict)
    finished_match_data['Match Result'] = finished_match_data.apply(calculate_match_result, axis=1)
    calculation_match_data['Match Result'] = calculation_match_data.apply(calculate_calculation_match_result, axis = 1)
    return finished_match_data, calculation_match_data, calculation_goals_for, calculation_goals_against

def calculate_calculation_match_result(row):
    goals_for = row['Goals For']
    goals_against = row['Goals Against']
    if goals_for > goals_against:
        return 2
    elif goals_for < goals_against:
        return 0
    else:
        penalties_for = row["Penalties For"]
        penalties_against = row["Penalties Against"]
        if penalties_for > penalties_against:
            return 2
        elif penalties_for < penalties_against:
            return 0
        else:
            return 1

def calculate_match_result(row):
    goals_for = row['Goals For']
    goals_against = row['Goals Against']
    if type(goals_for) != int and '(' in goals_for:
        goals_for_value = int(goals_for[:goals_for.index('(')])
    else:
        goals_for_value = int(goals_for)
    if type(goals_against) != int and '(' in goals_against:
        goals_against_value = int(goals_against[:goals_against.index('(')])
    else:
         goals_against_value = int(goals_against)


    if goals_for_value > goals_against_value:
        return "Win"
    elif goals_for_value < goals_against_value:
        return "Loss"
    else:
        goals_for_in_brackets = int(goals_for.split(' ')[1].strip('()')) if '(' in str(goals_for) else 0
        goals_against_in_brackets = int(goals_against.split(' ')[1].strip('()')) if '(' in str(goals_against) else 0
        
        if goals_for_in_brackets > goals_against_in_brackets:
            return "Win"
        elif goals_for_in_brackets < goals_against_in_brackets:
            return "Loss"
        return "Draw"

def get_future_matches(selected_team):
    print(f"https://fbref.com/en/squads/{team_and_keys[selected_team][0]}/2023-2024/{selected_team}-Stats")
    HTML_markup = requests.get(f"https://fbref.com/en/squads/{team_and_keys[selected_team][0]}/2023-2024/{selected_team}-Stats").text
    parsed_code = BeautifulSoup(HTML_markup, 'html.parser')
    date_elements = parsed_code.find_all("th", {"data-stat": "date"})
    dates = []
    
    goals_for_elements = parsed_code.find_all("td", {"data-stat": "goals_for"})
    
    goals_against_elements = parsed_code.find_all("td", {"data-stat": "goals_against"})
    
    opponent_elements = parsed_code.find_all("td", {"data-stat": "opponent"})
    opponents = []
    
    venue_elements = parsed_code.find_all("td", {"data-stat":"venue"})
    venues = []
    
    for date_element, goals_for_element, goals_against_element, opponent_element, venue_element in zip(date_elements, goals_for_elements, goals_against_elements, opponent_elements, venue_elements):
        date = date_element.a.get_text() if date_element.a else date_element.get_text()
        goals_for = goals_for_element.get_text()
        goals_against = goals_against_element.get_text()
        opponent = opponent_element.a.get_text() if opponent_element.a else opponent_element.get_text()
        venue = venue_element.get_text() 
        opponent = opponent.split(' ')
        text = ""
        for value in opponent:
            if value == "Utd":
                text = text+"United-"
            elif value == "Nott'ham":
                text = text + "Nottingham-"
            else:
                text = text + value + "-"
        
        opponent = text[:(len(text)-1)]
        opponent = opponent.replace(" ", "-")
        if opponent in team_and_keys.keys() and venue and opponent and goals_for == "" and goals_against == "":
            dates.append(date)
            opponents.append(opponent)
            venues.append(venue)
        
    data_dict = {
        "Date": dates,
        "Opponents": opponents,
        "Venue": venues
    }

    return pd.DataFrame(data_dict)
    
    

def predict_values(match_data):
    goals_for_predictor = DecisionTreeClassifier()
    goals_against_predictor = DecisionTreeClassifier()
    training_match_data = match_data.drop(columns=["Goals For", "Goals Against", "Penalties For", "Penalties Against", "Match Result"])
    st.dataframe(training_match_data)
    st.dataframe(match_data)
    goals_for_predictor.fit(training_match_data, match_data["Goals For"])
    goals_against_predictor.fit(training_match_data, match_data["Goals Against"])

    return goals_for_predictor, goals_against_predictor

def process_input(selected_team):
    if selected_team in team_and_keys.keys():
        finished_match_data, calculation_match_data, calculation_goals_for, calculation_goals_against = getGameHistory(selected_team)
        goals_for_predictor, goals_against_predictor = predict_values(calculation_match_data)
        future_matches = get_future_matches(selected_team)
        training_future_matches = pd.DataFrame()
        training_future_matches["Date"] = future_matches["Date"].apply(convertDate)
        training_future_matches["Opponents"] = future_matches['Opponents'].map(lambda team: team_and_keys.get(team, [None, None])[1])
        training_future_matches["Venue"] = future_matches["Venue"].apply(getVenue)
        st.dataframe(future_matches)
        st.dataframe(training_future_matches)
        future_matches['Goals For'] = goals_for_predictor.predict(training_future_matches)
        future_matches['Goals Against'] = goals_against_predictor.predict(training_future_matches)
        future_matches['Match Result'] = future_matches.apply(calculate_match_result, axis=1)
        st.dataframe(future_matches)

    elif selected_team is not None:
        st.warning("Team not found. Please enter a valid Premier League team.")

def main():
    st.title("Premier League Team Selector")

    # Use st.form to create a form
    with st.form("team_selector_form"):
        # Get user input
        selected_team = st.text_input("Enter a Premier League team [Ensure the beginning of each word is Capitalized (Eg: Tottenham Hotspur not tottenham hotspur)]:")
        selected_team = selected_team.split(' ')
        text = ""
        for val in selected_team:
            text = text + val + "-"
        
        selected_team = text[0:len(text)-1]
        # Add a Submit button to the form
        submit_button = st.form_submit_button("Submit")

    # Check if the form is submitted
    if submit_button:
        # Process the user input when the button is clicked
        process_input(selected_team)


if __name__ == "__main__":
    main()


