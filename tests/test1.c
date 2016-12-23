int main() {
    char str[10001];
    gets(str);
    int j = strlen(str);
    int i = 0;
    int mid = j / 2;
    j = j - 1;

    if (j < 0) {
        printf("%s\n", "ERROR");
        return 0;
    }

    while ((i < mid) && (str[i] == str[j])) {
        i = i + 1;
        j = j - 1;
    }
    if (i == mid) 
        printf("%s\n", "True");
    else
        printf("%s\n", "False");
    return 0;
}
