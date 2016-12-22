int lessPrior[6][6] = {{1, 1, 1, 1, 0, 1}, {1, 1, 1, 1, 0, 1},
    {0, 0, 1, 1, 0, 1}, {0, 0, 1, 1, 0, 1},
    {0, 0, 0, 0, 0, 1}, {1, 1, 1, 1, 0, 1}};

struct SqStack {
    int val[1000];
    int cur;
} op, value;

void init(struct SqStack *stk) { stk->cur = 0; }

void push(struct SqStack *stk, int n) { stk->val[stk->cur++] = n; }

int pop(struct SqStack *stk) { return stk->val[--stk->cur]; }

int top(struct SqStack *stk) { return stk->val[stk->cur - 1]; }

int isEmpty(struct SqStack *stk) { return stk->cur == 0; }

int indexOf(char ch) {
    if (ch=='+') return 0;
    else {
        if (ch=='-') return 1;
        else {
            if (ch=='*') return 2;
            else {
                if (ch=='/') return 3;
                else {
                    if (ch=='(') return 4;
                    else {
                        if (ch==')') return 5;
                        else return -1;
                    }
                }
            }
        }
    }
}

void sendOp(char op) {
    if (op == '(' || op == ')')
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
}

int main() {
    init(&value);
    init(&op);
    char str[101]="1+(5-2)*4/(2+1)";
    int i = 0;
    while (str[i]) {
        if (isdigit(str[i])) {
            int j = i;
            while( str[i] && isdigit(str[i])) {i++;}
            char buff[11] = {};
            memcpy(buff, str + j, i - j);
            push(&value, atoi(buff));
            continue;
        }
        while (!isEmpty(&op) && lessPrior[indexOf(str[i])][indexOf(top(&op))])
            sendOp(pop(&op));
        if (str[i] == ')' && top(&op) == '(') {
            pop(&op);
            i++;
            continue;
        }
        if (str[i] == '-' &&
            (!i || ((!isdigit(str[i - 1]) && str[i - 1] != ')'))))
            push(&value, 0);
        push(&op, str[i++]);
    }
    while (!isEmpty(&op))
        sendOp(pop(&op));
    printf("%d\n", pop(&value));
    return 0;
}
