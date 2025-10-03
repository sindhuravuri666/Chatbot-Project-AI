from ortools.linear_solver import pywraplp

# Toy dataset: city -> (cost, travel_hours)
cities = {
    "Paris": (200, 2),
    "London": (250, 3),
    "Rome": (300, 4),
    "Berlin": (180, 3),
    "Madrid": (220, 2)
}

def plan_trip(constraints):
    budget = constraints.get("budget", 9999)
    days = constraints.get("days", 3)
    must_include = constraints.get("must_include", [])

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return None

    x = {city: solver.BoolVar(city) for city in cities}

    # constraint: total days
    solver.Add(sum(x[city] for city in cities) == days)

    # constraint: budget
    solver.Add(sum(cities[city][0] * x[city] for city in cities) <= budget)

    # must include cities
    for m in must_include:
        if m in cities:
            solver.Add(x[m] == 1)

    # objective: minimize travel hours (toy objective)
    solver.Minimize(sum(cities[city][1] * x[city] for city in cities))

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        selected = [city for city in cities if x[city].solution_value() == 1]
        total_cost = sum(cities[c][0] for c in selected)
        total_hours = sum(cities[c][1] for c in selected)
        return {"plan": selected, "cost": total_cost, "hours": total_hours}
    else:
        return None
