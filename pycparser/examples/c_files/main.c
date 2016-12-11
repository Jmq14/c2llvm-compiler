//
//  main.c
//  Expressions
//
//  Created by 王永赫 on 15/10/14.
//  Copyright © 2015年 THSS. All rights reserved.
//

#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

#define MaxDepth 1000

static const int lessPrior[][6] = { // lessPrior[new][toCompare];
    {1, 1, 1, 1, 0, 1},             // value 0 -> push; value 1 -> pop;
    {1, 1, 1, 1, 0, 1},
    {0, 0, 1, 1, 0, 1},
    {0, 0, 1, 1, 0, 1},
    {0, 0, 0, 0, 0, 1},
    {1, 1, 1, 1, 0, 1}
};

struct SqStack {
    double val[MaxDepth];
    int cur;
} op, value;

typedef struct SqStack SqStack;

void init(SqStack *stk) {
    stk->cur = 0;
}

void push(SqStack *stk, double n) {
    stk->val[stk->cur++] = n;
}

double pop(SqStack *stk) {
    return stk->val[--stk->cur];
}

double top(SqStack *stk) {
    return stk->val[stk->cur - 1];
}

int isEmpty(SqStack *stk) {
    return stk->cur == 0;
}

int indexOf(char ch) {
    switch (ch) {
        case '+': return 0;
        case '-': return 1;
        case '*': return 2;
        case '/': return 3;
        case '(': return 4;
        case ')': return 5;
        default: return -1;
    }
}

void sendOp(char op) {
    if (op == '(' || op == ')')
        return;
    double right = pop(&value);
    switch (op) {
        case '+':
            push(&value, pop(&value) + right);
            break;
        case '-':
            push(&value, pop(&value) - right);
            break;
        case '*':
            push(&value, pop(&value) * right);
            break;
        case '/':
            push(&value, pop(&value) / right);
            break;
    }
}

int main(int argc, const char * argv[]) {
    init(&value);
    init(&op);
    char str[101];
    scanf("%s", str);
    int i = 0;
    while (str[i]) {
        if (isdigit(str[i])) {
            int j = i;
            for (; str[i] && isdigit(str[i]); i++)
                ;
            char buff[11] = {};
            memcpy(buff, str + j, i - j);
            push(&value, atof(buff));
            continue;
        }
        while (!isEmpty(&op) && lessPrior[indexOf(str[i])][indexOf((char)top(&op))])
            sendOp((char)pop(&op));
        if (str[i] == ')' && (char)top(&op) == '(') {
            pop(&op);
            i++;
            continue;
        }
        if (str[i] == '-' && (!i || ((!isdigit(str[i - 1]) && str[i - 1] != ')'))))
            push(&value, 0);
        push(&op, str[i++]);
    }
    while (!isEmpty(&op))
        sendOp((char)pop(&op));
    printf("%.2f\n", pop(&value));
    return 0;
}
