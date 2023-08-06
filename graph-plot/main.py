from populateGraphWithCallStack import createWebGraphWithCallStack
import networkx as nx
import os


def main():
    # createWebGraph("nbcnews.com")
    # createGraphFeatures("forbes.com")
    fold = os.listdir("server/output")
    count = 0
    for f in fold:
        try:
            print("graph-plot: ", f)
            createWebGraphWithCallStack(f)
            count += 1
            with open("graph_logs.txt", "w") as log:
                log.write(str(count))
                log.close()
        except:
            print("not-graph-plot: ", f)


if __name__ == "__main__":
    main()
