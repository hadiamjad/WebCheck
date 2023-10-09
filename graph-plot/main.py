import os
from joblib import Parallel, delayed
from populateGraphWithCallStack import createWebGraphWithCallStack
lst = [0]
def process_folder(folder):
    fold = "/home/grads/hadiamjad/repositories/speed-graph/server/output/" + folder
    graph_pdf_path = os.path.join(fold, "graph.pdf")

    print(graph_pdf_path)
    # Check if the graph PDF file already exists
    if os.path.exists(graph_pdf_path):
        print("graph.pdf already exists in folder:", folder)
        lst[0] += 1
        with open("graph_logs.txt", "w") as count_file:
            count_file.write(str(lst[0]))
        return None  # Skip this folder

    print("Starting graph-plot for folder:", folder)
    try:
        createWebGraphWithCallStack(folder)
        print("Completed graph-plot for folder:", folder)
        # Increment the counter after successful processing
        lst[0] += 1
        # Log the updated count to a file
        with open("graph_logs.txt", "w") as count_file:
            count_file.write(str(lst[0]))
    except Exception as e:
        print("Error processing folder:", folder, e)
    return folder

def main():
    folders = os.listdir("server/output")
    num_jobs = len(folders)
    num_parallel_jobs = -1  # Use all available CPU cores

    results = Parallel(n_jobs=num_parallel_jobs)(
        delayed(process_folder)(folder) for folder in folders
    )

if __name__ == "__main__":
    main()
