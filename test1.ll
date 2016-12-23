define i32 @"main"() 
{
entry:
  %"str" = alloca [10001 x i8]
  %".2" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"str", i32 0, i32 0
  %".3" = call i32 (...) @"gets"(i8* %".2")
  %"j" = alloca i32
  %".4" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"str", i32 0, i32 0
  %".5" = call i32 (i8*) @"strlen"(i8* %".4")
  store i32 %".5", i32* %"j"
  %"i" = alloca i32
  store i32 0, i32* %"i"
  %"mid" = alloca i32
  %".8" = load i32, i32* %"j"
  %".9" = sdiv i32 %".8", 2
  store i32 %".9", i32* %"mid"
  %".11" = load i32, i32* %"j"
  %".12" = sub i32 %".11", 1
  store i32 %".12", i32* %"j"
  %".14" = load i32, i32* %"j"
  %".15" = icmp slt i32 %".14", 0
  %".16" = icmp ne i1 %".15", 0
  br i1 %".16", label %"entry.if", label %"entry.endif"
entry.if:
  %".18" = getelementptr inbounds [4 x i8], [4 x i8]* @".str0", i32 0, i32 0
  %".19" = getelementptr inbounds [6 x i8], [6 x i8]* @".str1", i32 0, i32 0
  %".20" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".19")
  ret i32 0
entry.endif:
  br label %".22"
.22:
  %".26" = load i32, i32* %"i"
  %".27" = load i32, i32* %"mid"
  %".28" = icmp slt i32 %".26", %".27"
  %".29" = load i32, i32* %"i"
  %".30" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"str", i32 0, i32 %".29"
  %".31" = load i8, i8* %".30"
  %".32" = load i32, i32* %"j"
  %".33" = getelementptr inbounds [10001 x i8], [10001 x i8]* %"str", i32 0, i32 %".32"
  %".34" = load i8, i8* %".33"
  %".35" = icmp eq i8 %".31", %".34"
  %".36" = icmp ne i1 %".28", 0
  %".37" = icmp ne i1 %".35", 0
  %".38" = and i1 %".36", %".37"
  %".39" = icmp ne i1 %".38", 0
  br i1 %".39", label %".23", label %".24"
.23:
  %".41" = load i32, i32* %"i"
  %".42" = add i32 %".41", 1
  store i32 %".42", i32* %"i"
  %".44" = load i32, i32* %"j"
  %".45" = sub i32 %".44", 1
  store i32 %".45", i32* %"j"
  br label %".22"
.24:
  %".48" = load i32, i32* %"i"
  %".49" = load i32, i32* %"mid"
  %".50" = icmp eq i32 %".48", %".49"
  %".51" = icmp ne i1 %".50", 0
  br i1 %".51", label %".24.if", label %".24.else"
.24.if:
  %".53" = getelementptr inbounds [4 x i8], [4 x i8]* @".str2", i32 0, i32 0
  %".54" = getelementptr inbounds [5 x i8], [5 x i8]* @".str3", i32 0, i32 0
  %".55" = call i32 (i8*, ...) @"printf"(i8* %".53", i8* %".54")
  br label %".24.endif"
.24.else:
  %".57" = getelementptr inbounds [4 x i8], [4 x i8]* @".str4", i32 0, i32 0
  %".58" = getelementptr inbounds [6 x i8], [6 x i8]* @".str5", i32 0, i32 0
  %".59" = call i32 (i8*, ...) @"printf"(i8* %".57", i8* %".58")
  br label %".24.endif"
.24.endif:
  ret i32 0
}

declare i32 @"gets"(...) 

declare i32 @"strlen"(i8* %".1") 

@".str0" = constant [4 x i8] c"%s\0a\00"
@".str1" = constant [6 x i8] c"ERROR\00"
declare i32 @"printf"(i8* %".1", ...) 

@".str2" = constant [4 x i8] c"%s\0a\00"
@".str3" = constant [5 x i8] c"True\00"
@".str4" = constant [4 x i8] c"%s\0a\00"
@".str5" = constant [6 x i8] c"False\00"

