int current_counter = 0;
int unit_id_range = 5000;
int read_frame = -1;  //unit_id_range * 4;  //4 bits for each integer
int total_offset = 0;
int object_count  = 0;
int rolling_seconds = 5;
  //rolling_seconds * read_frame;
int unit_change = 0;
int unit_array = -1;
int change_array = -1;
int last_value = 0;


int xsArrayCreateInt2D(int m = 0, int n = 0, int defaultValue = 0)
{
    static int uid = 0;
    int arrayId = xsArrayCreateInt(m, -1, "uniquename"+uid);
    uid++;
    for(i = 0; < m)
    {
        xsArraySetInt(arrayId, i, xsArrayCreateInt(n, defaultValue, "uniquename"+uid));
        uid++;
    }
    return (arrayId);
}

void xsArraySetInt2D(int arrayID = -1, int m = -1, int n = -1, int value = 0) {
    int rowID = xsArrayGetInt(arrayID, m);
    xsArraySetInt(rowID, n, value);
}

int xsArrayGetInt2D(int arrayId = -1, int m = -1, int n = -1)
{
    int rowID = xsArrayGetInt(arrayId, m);
    return (xsArrayGetInt(rowID, n));
}

int xsArrayGetIntRows(int arrayID = -1)
{
    return (xsArrayGetSize(arrayID));
}

int xsArrayGetIntColumns(int arrayID = -1)
{
    return (xsArrayGetSize(xsArrayGetInt(arrayID, 0)));
}

void xsArrayAddIntRow2D(int arrayId = -1)
{
    xsArrayResizeInt(arrayId, xsArrayGetIntRows(arrayId) + 1);
}

void xsArrayIntRemoveRow2D(int arrayId = -1)
{
    xsArrayResizeInt(arrayId, xsArrayGetIntRows(arrayId) - 1);
}

void printArray(int arrayId = -1)
{
    static int print_id = 0;
    int row = 0;
    int col = 0;
    while(row < xsArrayGetIntRows(arrayId))
    {
        col = 0;
        string rowStr = "p" + print_id + " " + row + " [ ";
            while(col < xsArrayGetIntColumns(arrayId))
            {
                rowStr = rowStr + ""+ xsArrayGetInt2D(arrayId, row, col) + " ";
                col++;
            }
        rowStr = rowStr + "]";
        xsChatData(rowStr);
        print_id++;
        row++;
    }
}

void main(){
xsCreateFile(false);
//for (x=0;< ((unit_id_range) * rolling_seconds)) {
//    xsWriteInt(0);
//}
xsCloseFile();
//unit_array = xsArrayCreateInt(unit_id_range, 0, "unitarray1234");
unit_array = xsArrayCreateInt2D(rolling_seconds, unit_id_range, 0);
change_array = xsArrayCreateInt2D(rolling_seconds, unit_id_range, 0);
}

rule unit_logger
active
mininterval 1
{
    read_frame = unit_id_range * 4;  //4 bytes for each integer
    total_offset = 0;
    object_count  = 0;
    rolling_seconds = 5;
    xsCreateFile(false);
    for (id=0; <unit_id_range) {
        last_value = xsArrayGetInt2D(unit_array, rolling_seconds-1, id);
        object_count  = 0;
        for (p=0; <9) {
            object_count = object_count + xsGetObjectCount(p, id);
        }
        unit_change = last_value - object_count;
        for (c=0;<(rolling_seconds-1)){
            xsArraySetInt2D(unit_array, c,  id, xsArrayGetInt2D(unit_array, c+1, id));
            xsArraySetInt2D(change_array, c,  id, xsArrayGetInt2D(change_array, c+1, id));
        }
        xsArraySetInt2D(unit_array, rolling_seconds -1, id, object_count);
        xsArraySetInt2D(change_array, rolling_seconds -1, id, unit_change);
    }
    for (c=0;<rolling_seconds) {
        total_offset = c * read_frame;
        for (idx=0;<unit_id_range){
            //xsSetFilePosition(idx*4+total_offset);
            xsWriteInt(xsArrayGetInt2D(unit_array, c, idx));
        }
    //printArray(unit_array);
    }
    xsCloseFile();

}