import plotly as plt

def get_dicom_full_total(df_source):

    file_column_list = df_source[['dicom file name']].values.tolist()
    non_dup_file_column_list = []

    for i in file_column_list:
        if i not in non_dup_file_column_list:
            non_dup_file_column_list.append(i)

    total_dicom_images = len(non_dup_file_column_list)

    return total_dicom_images


def plot_reader_group_totals(total_subjects, total_sessions, dicom_total_full):
    y = ["patient ID", "accession number", "total DICOM images"]

    # getting values against each value of y
    x = [total_subjects, total_sessions, dicom_total_full]
    plt.barh(y, x)

    # setting label of y-axis
    plt.ylabel("patient information")

    # setting label of x-axis
    plt.xlabel("Reader group total")
    plt.title("dicom stats")

    return plt


def plot_read_status(df_source):
    unread_count = len(df_source.loc[(df_source['status'] == "unread")])
    normal = len(df_source.loc[(df_source['status'] == "normal read")])
    cant_read = len(df_source.loc[(df_source['status'] == "uninteretable")])
    roi_containing = len(df_source.loc[(df_source['status'] == "roi presesnt")])
    image_status = ["Unread", "Normal Findings", "Unreadable Image", "ROI containing"]
    totals = [unread_count, normal, cant_read, roi_containing]
    fig = plt.figure(figsize=(10, 7))
    plt.pie(totals, labels=image_status)

    return plt, unread_count, normal, cant_read, roi_containing

