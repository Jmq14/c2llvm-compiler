int lessPrior[6][6] = {{1, 1, 1, 1, 0, 1}, {1, 1, 1, 1, 0, 1},
    {0, 0, 1, 1, 0, 1}, {0, 0, 1, 1, 0, 1},
    {0, 0, 0, 0, 0, 1}, {1, 1, 1, 1, 0, 1}};

struct SqStack {
    int val[1000];
    int cur;
} op, value;

void init(struct SqStack *stk) { stk->cur = 0; return;}

void push(struct SqStack *stk, int n) { 
    int i = stk->cur;
    stk->val[i] = n; 
    stk->cur = stk->cur + 1;
    return;
}

int pop(struct SqStack *stk) { 
    stk->cur = stk->cur - 1;
    return stk->val[stk->cur]; 
}

int top(struct SqStack *stk) { return stk->val[stk->cur - 1]; }

int isEmpty(struct SqStack *stk) { return stk->cur == 0; }

int indexOf(char ch) {
    int index;
    if (ch=='+') index = 0;
    else {
        if (ch=='-') index = 1;
        else {
            if (ch=='*') index = 2;
            else {
                if (ch=='/') index = 3;
                else {
                    if (ch=='(') index = 4;
                    else {
                        if (ch==')') index = 5;
                        else index = 233;
                    }
                }
            }
        }
    }
    return index;
}

void sendOp(char op) {
    if ((op == '(') || (op == ')'))
        return;
    int right = pop(&value);
    if (op=='+') push(&value, pop(&value) + right);
    else {
        if (op=='-') push(&value, pop(&value) - right);
        else {
            if (op=='*') push(&value, pop(&value) * right);
            else {
                if (op=='/') push(&value, pop(&value) / right);
            }
        }
    }
    return;
}

int main() {
    init(&value);
    init(&op);
    char str[101];
    gets(str);
    int i = 0;
    while (str[i]) {
        if (isdigit(str[i])) {
            int j = i;
            while( str[i] && isdigit(str[i])) {i = i + 1;}
            char buff[11];
            memcpy(buff, str + j, i - j);
            push(&value, atoi(buff));
            continue;
        }
        while (!isEmpty(&op) && lessPrior[indexOf(str[i])][indexOf(top(&op))]){
            sendOp(pop(&op));
        }
        if ((str[i] == ')') && (top(&op) == '(')) {
            pop(&op);
            i = i + 1;
            continue;
        }
        if ((str[i] == '-') &&
            (!i || ((!isdigit(str[i - 1]) && (str[i - 1] != ')')))))
            push(&value, 0);
        push(&op, str[i]);
        i = i + 1;
    }
    while (!isEmpty(&op))
        sendOp(pop(&op));
    int out = pop(&value);
    printf("%d\n", out);
    return 0;
}
