%"SqStack" = type {[1000 x i32], i32}
@"lessPrior" = global [6 x [6 x i32]] [[6 x i32] [i32 1, i32 1, i32 1, i32 1, i32 0, i32 1], [6 x i32] [i32 1, i32 1, i32 1, i32 1, i32 0, i32 1], [6 x i32] [i32 0, i32 0, i32 1, i32 1, i32 0, i32 1], [6 x i32] [i32 0, i32 0, i32 1, i32 1, i32 0, i32 1], [6 x i32] [i32 0, i32 0, i32 0, i32 0, i32 0, i32 1], [6 x i32] [i32 1, i32 1, i32 1, i32 1, i32 0, i32 1]]
@"value" = common global %"SqStack" zeroinitializer, align 4
@"op" = common global %"SqStack" zeroinitializer, align 4
define void @"init"(%"SqStack"* %"stk") 
{
entry:
  %"stk.1" = alloca %"SqStack"*
  store %"SqStack"* %"stk", %"SqStack"** %"stk.1"
  %".4" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".5" = getelementptr inbounds %"SqStack", %"SqStack"* %".4", i32 0, i32 1
  store i32 0, i32* %".5"
  ret void
}

define void @"push"(%"SqStack"* %"stk", i32 %"n") 
{
entry:
  %"stk.1" = alloca %"SqStack"*
  store %"SqStack"* %"stk", %"SqStack"** %"stk.1"
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %"i" = alloca i32
  %".6" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".7" = getelementptr inbounds %"SqStack", %"SqStack"* %".6", i32 0, i32 1
  %".8" = load i32, i32* %".7"
  store i32 %".8", i32* %"i"
  %".10" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".11" = getelementptr inbounds %"SqStack", %"SqStack"* %".10", i32 0, i32 0
  %".12" = load i32, i32* %"i"
  %".13" = getelementptr inbounds [1000 x i32], [1000 x i32]* %".11", i32 0, i32 %".12"
  %".14" = load i32, i32* %"n.1"
  store i32 %".14", i32* %".13"
  %".16" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".17" = getelementptr inbounds %"SqStack", %"SqStack"* %".16", i32 0, i32 1
  %".18" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".19" = getelementptr inbounds %"SqStack", %"SqStack"* %".18", i32 0, i32 1
  %".20" = load i32, i32* %".19"
  %".21" = add i32 %".20", 1
  store i32 %".21", i32* %".17"
  ret void
}

define i32 @"pop"(%"SqStack"* %"stk") 
{
entry:
  %"stk.1" = alloca %"SqStack"*
  store %"SqStack"* %"stk", %"SqStack"** %"stk.1"
  %".4" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".5" = getelementptr inbounds %"SqStack", %"SqStack"* %".4", i32 0, i32 1
  %".6" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".7" = getelementptr inbounds %"SqStack", %"SqStack"* %".6", i32 0, i32 1
  %".8" = load i32, i32* %".7"
  %".9" = sub i32 %".8", 1
  store i32 %".9", i32* %".5"
  %".11" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".12" = getelementptr inbounds %"SqStack", %"SqStack"* %".11", i32 0, i32 0
  %".13" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".14" = getelementptr inbounds %"SqStack", %"SqStack"* %".13", i32 0, i32 1
  %".15" = load i32, i32* %".14"
  %".16" = getelementptr inbounds [1000 x i32], [1000 x i32]* %".12", i32 0, i32 %".15"
  %".17" = load i32, i32* %".16"
  ret i32 %".17"
}

define i32 @"top"(%"SqStack"* %"stk") 
{
entry:
  %"stk.1" = alloca %"SqStack"*
  store %"SqStack"* %"stk", %"SqStack"** %"stk.1"
  %".4" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".5" = getelementptr inbounds %"SqStack", %"SqStack"* %".4", i32 0, i32 0
  %".6" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".7" = getelementptr inbounds %"SqStack", %"SqStack"* %".6", i32 0, i32 1
  %".8" = load i32, i32* %".7"
  %".9" = sub i32 %".8", 1
  %".10" = getelementptr inbounds [1000 x i32], [1000 x i32]* %".5", i32 0, i32 %".9"
  %".11" = load i32, i32* %".10"
  ret i32 %".11"
}

define i32 @"isEmpty"(%"SqStack"* %"stk") 
{
entry:
  %"stk.1" = alloca %"SqStack"*
  store %"SqStack"* %"stk", %"SqStack"** %"stk.1"
  %".4" = load %"SqStack"*, %"SqStack"** %"stk.1"
  %".5" = getelementptr inbounds %"SqStack", %"SqStack"* %".4", i32 0, i32 1
  %".6" = load i32, i32* %".5"
  %".7" = icmp eq i32 %".6", 0
  %".8" = sext i1 %".7" to i32
  ret i32 %".8"
}

define i32 @"indexOf"(i8 signext %"ch") 
{
entry:
  %"ch.1" = alloca i8
  store i8 %"ch", i8* %"ch.1"
  %"index" = alloca i32
  %".4" = load i8, i8* %"ch.1"
  %".5" = icmp eq i8 %".4", 43
  %".6" = icmp ne i1 %".5", 0
  br i1 %".6", label %"entry.if", label %"entry.else"
entry.if:
  store i32 0, i32* %"index"
  br label %"entry.endif"
entry.else:
  %".10" = load i8, i8* %"ch.1"
  %".11" = icmp eq i8 %".10", 45
  %".12" = icmp ne i1 %".11", 0
  br i1 %".12", label %"entry.else.if", label %"entry.else.else"
entry.endif:
  %".47" = load i32, i32* %"index"
  ret i32 %".47"
entry.else.if:
  store i32 1, i32* %"index"
  br label %"entry.else.endif"
entry.else.else:
  %".16" = load i8, i8* %"ch.1"
  %".17" = icmp eq i8 %".16", 42
  %".18" = icmp ne i1 %".17", 0
  br i1 %".18", label %"entry.else.else.if", label %"entry.else.else.else"
entry.else.endif:
  br label %"entry.endif"
entry.else.else.if:
  store i32 2, i32* %"index"
  br label %"entry.else.else.endif"
entry.else.else.else:
  %".22" = load i8, i8* %"ch.1"
  %".23" = icmp eq i8 %".22", 47
  %".24" = icmp ne i1 %".23", 0
  br i1 %".24", label %"entry.else.else.else.if", label %"entry.else.else.else.else"
entry.else.else.endif:
  br label %"entry.else.endif"
entry.else.else.else.if:
  store i32 3, i32* %"index"
  br label %"entry.else.else.else.endif"
entry.else.else.else.else:
  %".28" = load i8, i8* %"ch.1"
  %".29" = icmp eq i8 %".28", 40
  %".30" = icmp ne i1 %".29", 0
  br i1 %".30", label %"entry.else.else.else.else.if", label %"entry.else.else.else.else.else"
entry.else.else.else.endif:
  br label %"entry.else.else.endif"
entry.else.else.else.else.if:
  store i32 4, i32* %"index"
  br label %"entry.else.else.else.else.endif"
entry.else.else.else.else.else:
  %".34" = load i8, i8* %"ch.1"
  %".35" = icmp eq i8 %".34", 41
  %".36" = icmp ne i1 %".35", 0
  br i1 %".36", label %"entry.else.else.else.else.else.if", label %"entry.else.else.else.else.else.else"
entry.else.else.else.else.endif:
  br label %"entry.else.else.else.endif"
entry.else.else.else.else.else.if:
  store i32 5, i32* %"index"
  br label %"entry.else.else.else.else.else.endif"
entry.else.else.else.else.else.else:
  store i32 233, i32* %"index"
  br label %"entry.else.else.else.else.else.endif"
entry.else.else.else.else.else.endif:
  br label %"entry.else.else.else.else.endif"
}

define void @"sendOp"(i8 signext %"op") 
{
entry:
  %"op.1" = alloca i8
  store i8 %"op", i8* %"op.1"
  %".4" = load i8, i8* %"op.1"
  %".5" = icmp eq i8 %".4", 40
  %".6" = load i8, i8* %"op.1"
  %".7" = icmp eq i8 %".6", 41
  %".8" = icmp ne i1 %".5", 0
  %".9" = icmp ne i1 %".7", 0
  %".10" = or i1 %".8", %".9"
  %".11" = icmp ne i1 %".10", 0
  br i1 %".11", label %"entry.if", label %"entry.endif"
entry.if:
  ret void
entry.endif:
  %"right" = alloca i32
  %".14" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"value")
  store i32 %".14", i32* %"right"
  %".16" = load i8, i8* %"op.1"
  %".17" = icmp eq i8 %".16", 43
  %".18" = icmp ne i1 %".17", 0
  br i1 %".18", label %"entry.endif.if", label %"entry.endif.else"
entry.endif.if:
  %".20" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"value")
  %".21" = load i32, i32* %"right"
  %".22" = add i32 %".20", %".21"
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"value", i32 %".22")
  br label %"entry.endif.endif"
entry.endif.else:
  %".25" = load i8, i8* %"op.1"
  %".26" = icmp eq i8 %".25", 45
  %".27" = icmp ne i1 %".26", 0
  br i1 %".27", label %"entry.endif.else.if", label %"entry.endif.else.else"
entry.endif.endif:
  ret void
entry.endif.else.if:
  %".29" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"value")
  %".30" = load i32, i32* %"right"
  %".31" = sub i32 %".29", %".30"
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"value", i32 %".31")
  br label %"entry.endif.else.endif"
entry.endif.else.else:
  %".34" = load i8, i8* %"op.1"
  %".35" = icmp eq i8 %".34", 42
  %".36" = icmp ne i1 %".35", 0
  br i1 %".36", label %"entry.endif.else.else.if", label %"entry.endif.else.else.else"
entry.endif.else.endif:
  br label %"entry.endif.endif"
entry.endif.else.else.if:
  %".38" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"value")
  %".39" = load i32, i32* %"right"
  %".40" = mul i32 %".38", %".39"
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"value", i32 %".40")
  br label %"entry.endif.else.else.endif"
entry.endif.else.else.else:
  %".43" = load i8, i8* %"op.1"
  %".44" = icmp eq i8 %".43", 47
  %".45" = icmp ne i1 %".44", 0
  br i1 %".45", label %"entry.endif.else.else.else.if", label %"entry.endif.else.else.else.endif"
entry.endif.else.else.endif:
  br label %"entry.endif.else.endif"
entry.endif.else.else.else.if:
  %".47" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"value")
  %".48" = load i32, i32* %"right"
  %".49" = sdiv i32 %".47", %".48"
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"value", i32 %".49")
  br label %"entry.endif.else.else.else.endif"
entry.endif.else.else.else.endif:
  br label %"entry.endif.else.else.endif"
}

define i32 @"main"() 
{
entry:
  call void (%"SqStack"*) @"init"(%"SqStack"* @"value")
  call void (%"SqStack"*) @"init"(%"SqStack"* @"op")
  %"str" = alloca [101 x i8]
  %".4" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 0
  %".5" = call i32 (...) @"gets"(i8* %".4")
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %".7"
.7:
  %".11" = load i32, i32* %"i"
  %".12" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".11"
  %".13" = load i8, i8* %".12"
  %".14" = icmp ne i8 %".13", 0
  br i1 %".14", label %".8", label %".9"
.8:
  %".16" = load i32, i32* %"i"
  %".17" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".16"
  %".18" = load i8, i8* %".17"
  %".19" = sext i8 %".18" to i32
  %".20" = call i32 (i32) @"isdigit"(i32 %".19")
  %".21" = icmp ne i32 %".20", 0
  br i1 %".21", label %".8.if", label %".8.endif"
.9:
  br label %".139"
.8.if:
  %"j" = alloca i32
  %".23" = load i32, i32* %"i"
  store i32 %".23", i32* %"j"
  br label %".25"
.8.endif:
  br label %".58"
.25:
  %".29" = load i32, i32* %"i"
  %".30" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".29"
  %".31" = load i8, i8* %".30"
  %".32" = load i32, i32* %"i"
  %".33" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".32"
  %".34" = load i8, i8* %".33"
  %".35" = sext i8 %".34" to i32
  %".36" = call i32 (i32) @"isdigit"(i32 %".35")
  %".37" = icmp ne i8 %".31", 0
  %".38" = icmp ne i32 %".36", 0
  %".39" = and i1 %".37", %".38"
  %".40" = icmp ne i1 %".39", 0
  br i1 %".40", label %".26", label %".27"
.26:
  %".42" = load i32, i32* %"i"
  %".43" = add i32 %".42", 1
  store i32 %".43", i32* %"i"
  br label %".25"
.27:
  %"buff" = alloca [11 x i8]
  %".46" = getelementptr inbounds [11 x i8], [11 x i8]* %"buff", i32 0, i32 0
  %".47" = load i32, i32* %"j"
  %".48" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 0
  %".49" = getelementptr inbounds i8, i8* %".48", i32 %".47"
  %".50" = load i32, i32* %"i"
  %".51" = load i32, i32* %"j"
  %".52" = sub i32 %".50", %".51"
  call void (i8*, i8*, i32, i32, i1) @"llvm.memcpy.p0i8.p0i8.i32"(i8* %".46", i8* %".49", i32 %".52", i32 1, i1 0)
  %".54" = getelementptr inbounds [11 x i8], [11 x i8]* %"buff", i32 0, i32 0
  %".55" = call i32 (...) @"atoi"(i8* %".54")
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"value", i32 %".55")
  br label %".7"
.58:
  %".62" = call i32 (%"SqStack"*) @"isEmpty"(%"SqStack"* @"op")
  %".63" = icmp eq i32 %".62", 0
  %".64" = load i32, i32* %"i"
  %".65" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".64"
  %".66" = load i8, i8* %".65"
  %".67" = call i32 (i8) @"indexOf"(i8 %".66")
  %".68" = getelementptr inbounds [6 x [6 x i32]], [6 x [6 x i32]]* @"lessPrior", i32 0, i32 %".67"
  %".69" = call i32 (%"SqStack"*) @"top"(%"SqStack"* @"op")
  %".70" = trunc i32 %".69" to i8
  %".71" = call i32 (i8) @"indexOf"(i8 %".70")
  %".72" = getelementptr inbounds [6 x i32], [6 x i32]* %".68", i32 0, i32 %".71"
  %".73" = load i32, i32* %".72"
  %".74" = icmp ne i1 %".63", 0
  %".75" = icmp ne i32 %".73", 0
  %".76" = and i1 %".74", %".75"
  %".77" = icmp ne i1 %".76", 0
  br i1 %".77", label %".59", label %".60"
.59:
  %".79" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"op")
  %".80" = trunc i32 %".79" to i8
  call void (i8) @"sendOp"(i8 %".80")
  br label %".58"
.60:
  %".83" = load i32, i32* %"i"
  %".84" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".83"
  %".85" = load i8, i8* %".84"
  %".86" = icmp eq i8 %".85", 41
  %".87" = call i32 (%"SqStack"*) @"top"(%"SqStack"* @"op")
  %".88" = icmp eq i32 %".87", 40
  %".89" = icmp ne i1 %".86", 0
  %".90" = icmp ne i1 %".88", 0
  %".91" = and i1 %".89", %".90"
  %".92" = icmp ne i1 %".91", 0
  br i1 %".92", label %".60.if", label %".60.endif"
.60.if:
  %".94" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"op")
  %".95" = load i32, i32* %"i"
  %".96" = add i32 %".95", 1
  store i32 %".96", i32* %"i"
  br label %".7"
.60.endif:
  %".99" = load i32, i32* %"i"
  %".100" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".99"
  %".101" = load i8, i8* %".100"
  %".102" = icmp eq i8 %".101", 45
  %".103" = load i32, i32* %"i"
  %".104" = icmp eq i32 %".103", 0
  %".105" = load i32, i32* %"i"
  %".106" = sub i32 %".105", 1
  %".107" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".106"
  %".108" = load i8, i8* %".107"
  %".109" = sext i8 %".108" to i32
  %".110" = call i32 (i32) @"isdigit"(i32 %".109")
  %".111" = icmp eq i32 %".110", 0
  %".112" = load i32, i32* %"i"
  %".113" = sub i32 %".112", 1
  %".114" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".113"
  %".115" = load i8, i8* %".114"
  %".116" = icmp ne i8 %".115", 41
  %".117" = icmp ne i1 %".111", 0
  %".118" = icmp ne i1 %".116", 0
  %".119" = and i1 %".117", %".118"
  %".120" = icmp ne i1 %".104", 0
  %".121" = icmp ne i1 %".119", 0
  %".122" = or i1 %".120", %".121"
  %".123" = icmp ne i1 %".102", 0
  %".124" = icmp ne i1 %".122", 0
  %".125" = and i1 %".123", %".124"
  %".126" = icmp ne i1 %".125", 0
  br i1 %".126", label %".60.endif.if", label %".60.endif.endif"
.60.endif.if:
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"value", i32 0)
  br label %".60.endif.endif"
.60.endif.endif:
  %".130" = load i32, i32* %"i"
  %".131" = getelementptr inbounds [101 x i8], [101 x i8]* %"str", i32 0, i32 %".130"
  %".132" = load i8, i8* %".131"
  %".133" = sext i8 %".132" to i32
  call void (%"SqStack"*, i32) @"push"(%"SqStack"* @"op", i32 %".133")
  %".135" = load i32, i32* %"i"
  %".136" = add i32 %".135", 1
  store i32 %".136", i32* %"i"
  br label %".7"
.139:
  %".143" = call i32 (%"SqStack"*) @"isEmpty"(%"SqStack"* @"op")
  %".144" = icmp eq i32 %".143", 0
  %".145" = icmp ne i1 %".144", 0
  br i1 %".145", label %".140", label %".141"
.140:
  %".147" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"op")
  %".148" = trunc i32 %".147" to i8
  call void (i8) @"sendOp"(i8 %".148")
  br label %".139"
.141:
  %"out" = alloca i32
  %".151" = call i32 (%"SqStack"*) @"pop"(%"SqStack"* @"value")
  store i32 %".151", i32* %"out"
  %".153" = getelementptr inbounds [4 x i8], [4 x i8]* @".str3", i32 0, i32 0
  %".154" = load i32, i32* %"out"
  %".155" = call i32 (i8*, ...) @"printf"(i8* %".153", i32 %".154")
  ret i32 0
}

declare i32 @"gets"(...) 

declare i32 @"isdigit"(i32 %".1") 

declare void @"llvm.memcpy.p0i8.p0i8.i32"(i8* %".1", i8* %".2", i32 %".3", i32 %".4", i1 %".5") 

declare i32 @"atoi"(...) 

@".str3" = constant [4 x i8] c"%d\0a\00"
declare i32 @"printf"(i8* %".1", ...) 
