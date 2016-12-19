struct _Stack{
    char *base;
    char *top;
    int size;
}s;

char STACK[20+1] = {0};

int StackInit(struct _Stack *s)
{
    if(NULL == s)
        return 1;

    s->top = s->base = &STACK[0];
    s->size = 0;
    return 0;

}
int StackDestroy(struct _Stack *s)
{
    int i =0;

    if(NULL == s)
        return 1;

    while(i<20)
    {
        STACK[i] = 0;
        i++;
    }
    s->top = s->base = NULL;
    s->size = 0;
    return 0;
}
int StackPrint(struct _Stack *s)
{
    int index = 0;

    if(NULL == s)
        return 1;

    if(s->size == 0)
    {
        printf("the Stack is empty,there is not any element \n");
        return 1;
    }

    while(index < (s->size))
    {
        printf("%d  ",*((s->base)+index) );
        index++;
    }

    printf("\n ");

    return 0;
}

int StackPush(struct _Stack *s, char e)
{
    if(NULL == s)
        return 1;

    if(s->size >= 20)
    {
        printf("the Stack is full \n");
        return 1;
    }

    *(s->top) = e;
    (s->top)++;
    (s->size)++;

    return 0;
}

int StackPop(struct _Stack *s, char *e)
{
    if(NULL == s)
        return 1;

    if(s->size == 0)
    {
        return 1;
    }

    (s->top)--;
    *e = *(s->top);
    (s->size)--;

    return 0;
}

int main()
{
    char ch = '\0';
    char str[2];
    char a1[20]= "1+2*3-6/3";
    char a2[20]={'\0'};
    int i,j;
    int a,b;
    int res = 0;
    int stack[20] ={0};

    i = j = a = b = 0;
    StackInit(&s);

    while(a1[i] != '\0')
    {
        printf("%c",a1[i]);

        if(a1[i] == '+' || a1[i] == '-')
        {
            if(s.size != 0)
            {
                while( s.size >= 0 && !StackPop(&s,&ch))
                {
                    a2[j] = ch;
                    ch = '\0';
                    j++;
                }
                StackPush( &s,a1[i] );
            }
            else
                StackPush(&s,a1[i]);
        }
        else if( a1[i] == '*' || a1[i] == '/')
        {
            if(s.size != 0)
            {
                if(!StackPop(&s,&ch))
                {
                    if(ch == '+' || ch == '-')
                    {
                        StackPush(&s,ch);
                        StackPush( &s,a1[i] );
                    }
                    else
                    {
                        StackPush(&s,ch);
                        while( !StackPop(&s,&ch) && (ch == '*' || ch == '/') )
                        {
                            a2[j] = ch;
                            ch = '\0';
                            j++;
                        }
                        StackPush( &s,a1[i] );
                    }
                }
            }
            else
                StackPush(&s,a1[i]);
        }
        else
        {
            a2[j] = a1[i];
            j++;
        }

        i++;
    }

    while( s.size >= 0 && !StackPop(&s,&ch))
    {
        a2[j] = ch;
        ch = '\0';
        j++;
    }
    a2[j] = '\0';

    i=j=0;
    StackDestroy(&s);
    StackInit(&s);

    while(a2[i] != '\0')
    {
        if(a2[i] == '+')
        {
            j--;
            a = stack[j];
            j--;
            b = stack[j];

            stack[j]= a+b;
            j++;
        }
        else if(a2[i] == '-')
        {
            j--;
            a = stack[j];
            j--;
            b = stack[j];

            stack[j]= b-a;
            j++;
        }
        else if(a2[i] == '*')
        {
            j--;
            a = stack[j];
            j--;
            b = stack[j];

            stack[j]= a*b;
            j++;
        }
        else if(a2[i] == '/')
        {
            j--;
            a = stack[j];
            j--;
            b = stack[j];

            stack[j]= b/a;
            j++;
        }
        else
        {
            str[0] =a2[i];
            str[1] ='\0';
            stack[j]= atoi(str);
            j++;
        }

        i++;
    }
    res =stack[0];

    printf(" = %d ",res);
    printf("\n");
    return 0;
}
