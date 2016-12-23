define i32 @"main"() 
{
entry:
  %"pattern" = alloca [10001 x i8]
  %"target" = alloca [10001 x i8]
  %"psize" = alloca i32
  %"tsize" = alloca i32
  %".2" = getelementptr inbounds [4 x i8], [4 x i8]* @".str0", i32 0, i32 0
  %".3" = getelementptr inbounds [15 x i8], [15 x i8]* @".str1", i32 0, i32 0
  %".4" = call i32 (i8*, ...) @"printf"(i8* %".2", i8* %".3")
  %".5" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"target", i32 0, i32 0
  %".6" = call i32 (...) @"gets"(i8* %".5")
  %".7" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"target", i32 0, i32 0
  %".8" = call i32 (i8*) @"strlen"(i8* %".7")
  store i32 %".8", i32* %"tsize"
  %".10" = getelementptr inbounds [4 x i8], [4 x i8]* @".str2", i32 0, i32 0
  %".11" = getelementptr inbounds [16 x i8], [16 x i8]* @".str3", i32 0, i32 0
  %".12" = call i32 (i8*, ...) @"printf"(i8* %".10", i8* %".11")
  %".13" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 0
  %".14" = call i32 (...) @"gets"(i8* %".13")
  %".15" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 0
  %".16" = call i32 (i8*) @"strlen"(i8* %".15")
  store i32 %".16", i32* %"psize"
  %"i" = alloca i32
  %"k" = alloca i32
  %".18" = sub i32 0, 1
  store i32 %".18", i32* %"k"
  %"i.1" = alloca i32
  store i32 1, i32* %"i.1"
  %"pi" = alloca [10001 x i32]
  %".21" = getelementptr inbounds [10001 x i32], [10001 x i32]* %"pi", i32 0, i32 0
  %".22" = load i32, i32* %"k"
  store i32 %".22", i32* %".21"
  br label %".24"
.24:
  %".28" = load i32, i32* %"i.1"
  %".29" = load i32, i32* %"psize"
  %".30" = icmp slt i32 %".28", %".29"
  %".31" = icmp ne i1 %".30", 0
  br i1 %".31", label %".25", label %".26"
.25:
  br label %".33"
.26:
  %".80" = sub i32 0, 1
  store i32 %".80", i32* %"k"
  store i32 0, i32* %"i.1"
  br label %".83"
.33:
  %".37" = load i32, i32* %"k"
  %".38" = sub i32 0, 1
  %".39" = icmp sgt i32 %".37", %".38"
  %".40" = load i32, i32* %"k"
  %".41" = add i32 %".40", 1
  %".42" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 %".41"
  %".43" = load i8, i8* %".42"
  %".44" = load i32, i32* %"i.1"
  %".45" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 %".44"
  %".46" = load i8, i8* %".45"
  %".47" = icmp ne i8 %".43", %".46"
  %".48" = icmp ne i1 %".39", 0
  %".49" = icmp ne i1 %".47", 0
  %".50" = and i1 %".48", %".49"
  %".51" = icmp ne i1 %".50", 0
  br i1 %".51", label %".34", label %".35"
.34:
  %".53" = load i32, i32* %"k"
  %".54" = getelementptr inbounds [10001 x i32], [10001 x i32]* %"pi", i32 0, i32 %".53"
  %".55" = load i32, i32* %".54"
  store i32 %".55", i32* %"k"
  br label %".33"
.35:
  %".58" = load i32, i32* %"i.1"
  %".59" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 %".58"
  %".60" = load i8, i8* %".59"
  %".61" = load i32, i32* %"k"
  %".62" = add i32 %".61", 1
  %".63" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 %".62"
  %".64" = load i8, i8* %".63"
  %".65" = icmp eq i8 %".60", %".64"
  %".66" = icmp ne i1 %".65", 0
  br i1 %".66", label %".35.if", label %".35.endif"
.35.if:
  %".68" = load i32, i32* %"k"
  %".69" = add i32 %".68", 1
  store i32 %".69", i32* %"k"
  br label %".35.endif"
.35.endif:
  %".72" = load i32, i32* %"i.1"
  %".73" = getelementptr inbounds [10001 x i32], [10001 x i32]* %"pi", i32 0, i32 %".72"
  %".74" = load i32, i32* %"k"
  store i32 %".74", i32* %".73"
  %".76" = load i32, i32* %"i.1"
  %".77" = add i32 %".76", 1
  store i32 %".77", i32* %"i.1"
  br label %".24"
.83:
  %".87" = load i32, i32* %"i.1"
  %".88" = load i32, i32* %"tsize"
  %".89" = icmp slt i32 %".87", %".88"
  %".90" = icmp ne i1 %".89", 0
  br i1 %".90", label %".84", label %".85"
.84:
  br label %".92"
.85:
  %".147" = getelementptr inbounds [2 x i8], [2 x i8]* @".str5", i32 0, i32 0
  %".148" = call i32 (i8*, ...) @"printf"(i8* %".147")
  ret i32 0
.92:
  %".96" = load i32, i32* %"k"
  %".97" = sub i32 0, 1
  %".98" = icmp sgt i32 %".96", %".97"
  %".99" = load i32, i32* %"k"
  %".100" = add i32 %".99", 1
  %".101" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 %".100"
  %".102" = load i8, i8* %".101"
  %".103" = load i32, i32* %"i.1"
  %".104" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"target", i32 0, i32 %".103"
  %".105" = load i8, i8* %".104"
  %".106" = icmp ne i8 %".102", %".105"
  %".107" = icmp ne i1 %".98", 0
  %".108" = icmp ne i1 %".106", 0
  %".109" = and i1 %".107", %".108"
  %".110" = icmp ne i1 %".109", 0
  br i1 %".110", label %".93", label %".94"
.93:
  %".112" = load i32, i32* %"k"
  %".113" = getelementptr inbounds [10001 x i32], [10001 x i32]* %"pi", i32 0, i32 %".112"
  %".114" = load i32, i32* %".113"
  store i32 %".114", i32* %"k"
  br label %".92"
.94:
  %".117" = load i32, i32* %"i.1"
  %".118" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"target", i32 0, i32 %".117"
  %".119" = load i8, i8* %".118"
  %".120" = load i32, i32* %"k"
  %".121" = add i32 %".120", 1
  %".122" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"pattern", i32 0, i32 %".121"
  %".123" = load i8, i8* %".122"
  %".124" = icmp eq i8 %".119", %".123"
  %".125" = icmp ne i1 %".124", 0
  br i1 %".125", label %".94.if", label %".94.endif"
.94.if:
  %".127" = load i32, i32* %"k"
  %".128" = add i32 %".127", 1
  store i32 %".128", i32* %"k"
  br label %".94.endif"
.94.endif:
  %".131" = load i32, i32* %"k"
  %".132" = load i32, i32* %"psize"
  %".133" = sub i32 %".132", 1
  %".134" = icmp eq i32 %".131", %".133"
  %".135" = icmp ne i1 %".134", 0
  br i1 %".135", label %".94.endif.if", label %".94.endif.endif"
.94.endif.if:
  %".137" = getelementptr inbounds [4 x i8], [4 x i8]* @".str4", i32 0, i32 0
  %".138" = load i32, i32* %"i.1"
  %".139" = load i32, i32* %"k"
  %".140" = sub i32 %".138", %".139"
  %".141" = call i32 (i8*, ...) @"printf"(i8* %".137", i32 %".140")
  br label %".94.endif.endif"
.94.endif.endif:
  %".143" = load i32, i32* %"i.1"
  %".144" = add i32 %".143", 1
  store i32 %".144", i32* %"i.1"
  br label %".83"
}

@".str0" = constant [4 x i8] c"%s\0a\00"
@".str1" = constant [15 x i8] c"Source string:\00"
declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"gets"(...) 

declare i32 @"strlen"(i8* %".1") 

@".str2" = constant [4 x i8] c"%s\0a\00"
@".str3" = constant [16 x i8] c"Pattern string:\00"
@".str4" = constant [4 x i8] c"%d \00"
@".str5" = constant [2 x i8] c"\0a\00"
