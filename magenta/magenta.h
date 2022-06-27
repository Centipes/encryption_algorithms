/* You should define ADD_EXPORTS *only* when building the DLL. */
#ifdef _WIN32
  #ifdef ADD_EXPORTS
    #define ADDAPI __declspec(dllexport)
  #else
    #define ADDAPI __declspec(dllimport)
  #endif

/* Define calling convention in one place, for convenience. */
  #define ADDCALL __cdecl

#else /* _WIN32 not defined. */

  /* Define with no value on non-Windows OSes. */
  #define ADDAPI
  #define ADDCALL

#endif

/* Make sure functions are exported with C linkage under C++ compilers. */
#ifdef __cplusplus
extern "C"
{
  #endif

  uint8_t A(uint8_t x, uint8_t y);
  void S(uint8_t *RK, uint8_t *a_out);
  void T(uint8_t *a);
  uint64_t C(uint8_t *a);
  uint64_t F(uint64_t R, uint64_t K);
  ADDAPI void ADDCALL feistel(uint64_t *L_in, uint64_t *R_in, uint64_t *keys, int keys_size);

  #ifdef __cplusplus
}
#endif
