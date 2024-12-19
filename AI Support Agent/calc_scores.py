import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    recall_score,
    precision_score,
    confusion_matrix,
)
import seaborn as sns
import matplotlib.pyplot as plt


def calculate_scores(true_values, predictions):
    true_priorities = [true["priority"] for true in true_values]
    true_departments = [true["department"] for true in true_values]

    ai_priorities = [ai["priority"] for ai in predictions]
    ai_departments = [ai["department"] for ai in predictions]

    priority_accuracy = accuracy_score(true_priorities, ai_priorities)
    department_accuracy = accuracy_score(true_departments, ai_departments)

    priority_f1 = f1_score(true_priorities, ai_priorities, average="weighted")
    department_f1 = f1_score(true_departments, ai_departments, average="weighted")

    recall_score_priorities = recall_score(
        true_priorities, ai_priorities, average="weighted"
    )
    precision_score_priorities = precision_score(
        true_priorities, ai_priorities, average="weighted"
    )

    recall_score_departments = recall_score(
        true_departments, ai_departments, average="weighted"
    )

    precision_score_departments = precision_score(
        true_departments, ai_departments, average="weighted"
    )

    department_scores = {
        "accuracy": department_accuracy,
        "f1": department_f1,
        "recall": recall_score_departments,
        "precision": precision_score_departments,
    }

    priority_scores = {
        "accuracy": priority_accuracy,
        "f1": priority_f1,
        "recall": recall_score_priorities,
        "precision": precision_score_priorities,
    }

    scores = {
        "Metric": ["Accuracy", "F1 Score", "Recall", "Precision"],
        "Priority": [
            priority_scores["accuracy"],
            priority_scores["f1"],
            priority_scores["recall"],
            priority_scores["precision"],
        ],
        "Department": [
            department_scores["accuracy"],
            department_scores["f1"],
            department_scores["recall"],
            department_scores["precision"],
        ],
    }

    return pd.DataFrame(scores)


def plot_confusion_matrix(true_values, predictions):
    true_priorities = [true["priority"] for true in true_values]
    true_departments = [true["department"] for true in true_values]

    ai_priorities = [ai["priority"] for ai in predictions]
    ai_departments = [ai["department"] for ai in predictions]

    cm = confusion_matrix(true_priorities, ai_priorities)
    cm_departments = confusion_matrix(true_departments, ai_departments)

    plt.subplot(1, 2, 1)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=[1, 2, 3],
        yticklabels=[1, 2, 3],
    )
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix for Priorities")

    plt.subplot(1, 2, 2)

    sns.heatmap(
        cm_departments,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Hardware", "Accounting", "Software"],
        yticklabels=["Hardware", "Accounting", "Software"],
    )
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix for Departments")

    plt.gcf().set_size_inches(20, 8)
    plt.show()
