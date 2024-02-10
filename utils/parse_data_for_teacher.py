import pandas as pd
from io import BytesIO


def format_df_to_string(df):
    for col in df.columns:
        if df[col].dtype != "datetime64[ns]":
            df[col] = df[col].astype(str)
    return df


def student_results_to_dataframe(student_results):
    df = pd.DataFrame.from_dict(student_results, orient="index")
    return format_df_to_string(df)


def student_logs_to_dataframe(student_logs):
    all_logs = []
    for student_id, logs in student_logs.items():
        for log in logs:
            log["student_id"] = student_id
        all_logs += logs

    df = pd.DataFrame(all_logs)
    df.set_index("student_id", inplace=True)
    return format_df_to_string(df)


def victoryna_to_dataframe(victoryna, teacher_id):
    victoryna["teacher_id"] = teacher_id
    df = pd.DataFrame.from_dict(victoryna, orient="index")
    return format_df_to_string(df)


def get_student_dataframe(user_data, allowed_students):
    filtered_user_data = {
        str(key): value["info"]
        for key, value in user_data.items()
        if str(key) in allowed_students
    }
    df = pd.DataFrame.from_dict(filtered_user_data, orient="index")
    return format_df_to_string(df)


def save_dataframes_to_excel(results_table, student_table, logs_table, victoryna_table):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        victoryna_table.to_excel(writer, sheet_name="General info", header=False)
        results_table.to_excel(writer, sheet_name="Results")
        student_table.to_excel(writer, sheet_name="Students")
        logs_table.to_excel(writer, sheet_name="Logs")
    output.seek(0)
    return output
