
#ifndef __HOOKLIB_H__
#define __HOOKLIB_H__

#include <Windows.h>
#include "HDE32/hde32.h"


BYTE* InlineHook( BYTE *where, BYTE *fake)
{
	DWORD length = 0;
	BYTE *backup = 0;
	DWORD dwOldProtect = 0;
	hde32s hs;

	do
	{
		length += hde32_disasm( where + length, &hs);
	} while ( length < 5);

	// backup
	backup = (BYTE *)VirtualAlloc( 0, length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	memcpy( backup, where, length);
	*(backup + length) = '\xE9';
	*(DWORD*)(backup + length + 1) = where - backup - 5;

	// hook
	VirtualProtect( where, length, PAGE_EXECUTE_READWRITE, &dwOldProtect);
	*where = '\xE9';
	*(DWORD*)(where+1) = fake - where - 5;
	VirtualProtect( where, length, dwOldProtect, &dwOldProtect);

	return backup;
}


DWORD EatHook(BYTE *hDLL, DWORD where, DWORD fake)
{
	PIMAGE_NT_HEADERS pNtHdr = 0;
	PIMAGE_EXPORT_DIRECTORY pEat = 0;
	DWORD *dwAddrs = 0;
	DWORD dwOldProtect = 0;

	if (((PIMAGE_DOS_HEADER)hDLL)->e_magic == IMAGE_DOS_SIGNATURE)
	{
		pNtHdr = (PIMAGE_NT_HEADERS)(hDLL + ((PIMAGE_DOS_HEADER)hDLL)->e_lfanew);
		if ( pNtHdr->Signature == IMAGE_NT_SIGNATURE)
		{
			pEat = (PIMAGE_EXPORT_DIRECTORY)(hDLL + pNtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);
			dwAddrs = (DWORD*)(hDLL + pEat->AddressOfFunctions);
			--dwAddrs;
			while ( *(++dwAddrs))
			{
				if ( *dwAddrs == where - (DWORD)hDLL)
				{
					VirtualProtect( dwAddrs, 4, PAGE_EXECUTE_READWRITE, &dwOldProtect);
					*dwAddrs = fake - (DWORD)hDLL;
					VirtualProtect( dwAddrs, 4, dwOldProtect, &dwOldProtect);
					return where;
				}
			}
		}
	}

	return 0;
}


DWORD IatHook(BYTE *hDLL, DWORD where, DWORD fake)
{
	PIMAGE_NT_HEADERS pNtHdr = 0;
	PIMAGE_IMPORT_DESCRIPTOR pIats = 0;
	DWORD *dwAddrs = 0;
	DWORD dwOldProtect = 0;

	if (((PIMAGE_DOS_HEADER)hDLL)->e_magic == IMAGE_DOS_SIGNATURE)
	{
		pNtHdr = (PIMAGE_NT_HEADERS)(hDLL + ((PIMAGE_DOS_HEADER)hDLL)->e_lfanew);
		if ( pNtHdr->Signature == IMAGE_NT_SIGNATURE)
		{
			pIats = (PIMAGE_IMPORT_DESCRIPTOR)(hDLL + pNtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
			--pIats;
			while ( (++pIats)->FirstThunk)
			{
				dwAddrs = (DWORD*)(hDLL + pIats->FirstThunk);
				--dwAddrs;
				while ( *(++dwAddrs))
				{
					if ( *dwAddrs == where)
					{
						VirtualProtect( dwAddrs, 4, PAGE_EXECUTE_READWRITE, &dwOldProtect);
						*dwAddrs = fake;
						VirtualProtect( dwAddrs, 4, dwOldProtect, &dwOldProtect);
						return where;
					}
				}
			}
		}
	}

	return 0;

}


#endif