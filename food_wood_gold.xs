
rule pool_resources
active
highfrequency
{
for (r=0;<=3) {
    setTeamRes(1,4,r);
    setTeamRes(5,8,r);
    }
}

float getRes(int p=-1,int r=-1){
   return(xsPlayerAttribute(p,r);
}

void setTeamRes(int pstart = -1, int pend = -1, int res = -1){
    float t_total = 0;
    int p_count = pend - pstart;
    for (p=pstart;<=pend) {
        t_total = t_total + getRes(p,r);
    }
    float bal = t_total/pcount;
    for (p=pstart;<=pend) {
        xsSetPlayerAttribute(p,res,bal);
    }

}