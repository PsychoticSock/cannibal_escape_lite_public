int unit_id_lower = 0;
int unit_id_upper = 4159;
int unit_array = -1;
int log_count = 0;
int on_time = 0;
int duty_cycle = 20;

void write_deltas(int ticks = 0, int unit_delta = 0, int id = 0, int object_count = 0, int current_log_count = 0){
    int new_log_position = (log_count * 16) + 4;
    //xsChatData("NewLogPosition: " + new_log_position + "current_log_count" + current_log_count);
    xsSetFilePosition(0);
    log_count = log_count + 1;
    xsWriteInt(log_count);
    xsSetFilePosition(new_log_position);
    xsWriteInt(ticks);
    xsWriteInt(unit_delta);
    xsWriteInt(id);
    xsWriteInt(object_count);
    //xsChatData("ticks: " + ticks + "  unit_delta: " + unit_delta + "  id: " + id + "  object_count: " + object_count);

}

int count_all(int id = 0){
    int object_count = 0;
    for (p=0; <9) {
        object_count = object_count + xsGetObjectCount(p, id);
    }
    return(object_count);
}

void initial_count(int current_ticks = 0){
for (id=unit_id_lower; <unit_id_upper) {
        int object_count  = 0;
        int unit_delta = 0;

        object_count = count_all(id);

        write_deltas(current_ticks, unit_delta, id, object_count, log_count);

        xsArraySetInt(unit_array, id, object_count);
    }
}

int calculate_delta(int object_count = 0, int id = 0){
    int last_value = xsArrayGetInt(unit_array, id);
    return (object_count - last_value);
}

int ticks = 0;
rule unit_logger
inactive
highfrequency
{
    int unit_delta = 0;
    int object_count  = 0;
    int last_value = 0;

    ticks = (ticks + 1);

    on_time = ticks%duty_cycle;

    if (on_time == 0) {
        xsCreateFile(true);
        if (xsGetFileSize() >= pow(10, 6)) {
            xsCloseFile();
            xsCreateFile(false);
            log_count = 0;
            initial_count(ticks);
        }

        for (id=unit_id_lower; <unit_id_upper) {

            object_count  = count_all(id);
            unit_delta = calculate_delta(object_count, id);

            if (unit_delta == 0) {
            continue;
            }
            else {
                xsSetFilePosition(log_count * 4 + 4);
                write_deltas(ticks, unit_delta, id, object_count, log_count);
            }
           xsArraySetInt(unit_array, id, object_count);
        }
        xsCloseFile();
    }
}

void shield(){
	xsSetPlayerAttribute(7, 255, 3976);
	xsSetPlayerAttribute(7, 256, 2);
	xsSetPlayerAttribute(7, 257, 2);
	xsSetPlayerAttribute(7, 258, 906);
	xsSetPlayerAttribute(7, 259, 5);
	xsSetPlayerAttribute(7, 260, 109);
	xsSetPlayerAttribute(7, 261, 100);
}

void main(){
xsCreateFile(false);
xsWriteInt(0);  //set array length to 0
unit_array = xsArrayCreateInt(unit_id_upper, 0, "unitarray1234");
initial_count(0);
xsCloseFile();
xsEnableRule("unit_logger");
shield();
}


