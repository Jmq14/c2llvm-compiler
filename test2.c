int main() {
    char target[10001], pattern[10001];
    int tsize, psize;
    printf("%s\n", "Source string:");
    gets(target);
    tsize = strlen(target);
    printf("%s\n", "Pattern string:");
    gets(pattern);
    psize = strlen(pattern);
    int i;
    
    int k = -1;
    int i = 1;
    int pi[10001];
    pi[0] = k;
    while(i < psize){
        while ((k > -1) && (pattern[k + 1] != pattern[i]))
            k = pi[k];
        if (pattern[i] == pattern[k + 1])
            k = k + 1;
        pi[i] = k;
        i = i + 1;
    }

    k = -1;
    i = 0;
    while(i < tsize) {
        while ((k > -1) && (pattern[k + 1] != target[i]))
            k = pi[k];
        if (target[i] == pattern[k + 1])
            k = k + 1;
        if (k == (psize - 1))
            printf("%d ", i - k);
        i = i + 1;
    }
    printf("\n");
    return 0;
}
