from fastapi import FastAPI
from pydantic import BaseModel
from ortools.linear_solver import pywraplp

app = FastAPI()

# Input Schema
class JobRequest(BaseModel):
    jobs: list[int]   # processing times of jobs
    machines: int     # number of machines

@app.post("/schedule")
def optimize_schedule(data: JobRequest):
    jobs = data.jobs
    machines = data.machines
    n = len(jobs)

    # Solver
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return {"error": "Solver not available"}

    # Decision variables: assign[i][j] = job i on machine j
    assign = {}
    for i in range(n):
        for j in range(machines):
            assign[i, j] = solver.BoolVar(f"assign_{i}_{j}")

    # Each job must be assigned to exactly 1 machine
    for i in range(n):
        solver.Add(sum(assign[i, j] for j in range(machines)) == 1)

    # Machine load (total processing time on each machine)
    load = [solver.Sum(jobs[i] * assign[i, j] for i in range(n)) for j in range(machines)]

    # Objective: minimize maximum load (makespan)
    makespan = solver.NumVar(0, solver.infinity(), "makespan")
    for j in range(machines):
        solver.Add(load[j] <= makespan)
    solver.Minimize(makespan)

    # Solve
    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return {"error": "No optimal solution found"}

    # Build result
    assignment = {f"Machine {j+1}": [i for i in range(n) if assign[i, j].solution_value() > 0.5]
                  for j in range(machines)}

    return {
        "assignment": assignment,
        "makespan": makespan.solution_value()
    }
