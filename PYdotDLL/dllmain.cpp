// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "stdafx.h"
#include <Python.h>
//#include <HookLib/HookLib.h>
extern "C" {
	#include "../HookLib/HookLib.h"
}

#pragma comment( linker, "/EXPORT:InlineHook=_InlineHook")
#pragma comment( linker, "/EXPORT:EatHook=_EatHook")

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{

	if ( DLL_PROCESS_ATTACH == ul_reason_for_call)
	{
		char dllpath[MAX_PATH] = {0};
		char pycode[1024*5] = {0};

		Py_Initialize();
		GetModuleFileNameA( hModule, dllpath, sizeof(dllpath));
		*strrchr( dllpath, '.') = 0;
		sprintf( pycode, "execfile('%s.py')", dllpath);

		PyRun_SimpleString(pycode);
		PyEval_SaveThread();

	}
	else if ( DLL_THREAD_ATTACH == ul_reason_for_call)
	{
		//Do something
	}

	return TRUE;
}

