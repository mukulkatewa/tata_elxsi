# MISRA-C++ Coding Rules

## Memory Management

1. **Rule 18.4.1: Dynamic Memory Allocation**
   All dynamic memory allocations must be paired with corresponding deallocations. This prevents memory leaks and ensures efficient resource management in automotive systems.

2. **Rule 18.5.2: Placement New**
   Placement new shall only be used with properly aligned and sized memory buffers. This ensures memory safety and prevents undefined behavior from misaligned access.

3. **Rule 5.0.3: Null Pointer Dereference**
   Pointers must be checked for null before dereferencing. This prevents crashes and undefined behavior from accessing invalid memory locations.

## Variable Initialization

4. **Rule 8.4.1: Variable Initialization**
   All variables must be initialized before use. This prevents undefined behavior from uninitialized memory access and ensures deterministic program behavior.

5. **Rule 8.5.2: Static Variable Initialization**
   Static variables with external linkage must be explicitly initialized. This ensures consistent initialization order and prevents dependency issues across translation units.

6. **Rule 9.3.1: Array Initialization**
   Arrays must be fully initialized or use designated initializers. This prevents accessing uninitialized array elements and ensures predictable behavior.

## Control Flow

7. **Rule 6.4.3: Switch Statement Default**
   All switch statements must have a default case. This ensures all possible values are handled and prevents unexpected behavior from unhandled cases.

8. **Rule 6.4.5: Switch Case Fall-through**
   Fall-through in switch statements must be explicitly documented with a comment. This makes intentional fall-through clear and prevents accidental bugs.

9. **Rule 6.5.2: Loop Counter Modification**
   Loop counters must not be modified within the loop body except in the loop expression. This prevents confusing control flow and makes loop behavior predictable.

10. **Rule 6.6.1: Goto Statement Usage**
    The goto statement shall not be used. This prevents spaghetti code and maintains clear, structured control flow that is easier to analyze and verify.

## Type Safety

11. **Rule 10.3.2: Explicit Type Casting**
    Explicit type casts must be used when converting between incompatible types. This ensures type safety and prevents implicit conversions that may lose data or precision.

12. **Rule 10.1.1: Implicit Integer Conversion**
    Implicit conversions between signed and unsigned integers are not allowed. This prevents unexpected behavior from sign extension and value wrapping.

13. **Rule 10.4.2: Floating Point Comparison**
    Floating point values must not be compared for exact equality. This accounts for floating point precision limitations and prevents incorrect comparisons.

14. **Rule 5.0.4: Enum Type Safety**
    Enum values must not be used in arithmetic operations without explicit casting. This maintains type safety and prevents treating enums as arbitrary integers.

15. **Rule 5.2.1: Identifier Uniqueness**
    Identifiers must be unique within their scope and not rely on case differences alone. This prevents confusion and ensures code clarity across different contexts.

## Function Design

16. **Rule 8.2.1: Function Parameter Names**
    Function declarations must include parameter names, not just types. This improves code readability and makes function interfaces self-documenting.

17. **Rule 8.4.4: Function Return Values**
    Functions with non-void return types must return a value on all code paths. This ensures consistent behavior and prevents undefined return values.

18. **Rule 7.1.2: Function Side Effects**
    Functions should minimize side effects and clearly document any state modifications. This makes code behavior predictable and easier to test and verify.

19. **Rule 8.3.1: Function Declarations**
    Functions must be declared before use with matching signatures. This enables proper type checking and prevents linkage errors.

20. **Rule 2.10.1: Function Complexity**
    Functions should have a cyclomatic complexity below 15. This ensures functions remain testable, maintainable, and easier to verify for correctness.

## Additional Safety Rules

21. **Rule 0.1.9: Dead Code Elimination**
    All code must be reachable and executable. Dead code should be removed as it indicates logic errors and increases maintenance burden.

22. **Rule 5.0.5: Bitwise Operations on Signed Types**
    Bitwise operations must not be performed on signed integer types. This prevents undefined behavior from sign bit manipulation and ensures portable code.

23. **Rule 12.1.1: Operator Precedence**
    Complex expressions must use parentheses to clarify operator precedence. This prevents misinterpretation and ensures the intended evaluation order.

24. **Rule 16.3.1: Exception Handling**
    Exception specifications must be used consistently and exceptions must be caught appropriately. This ensures robust error handling in safety-critical systems.

25. **Rule 17.0.1: Standard Library Usage**
    Only approved standard library functions may be used in safety-critical code. This ensures all dependencies are verified and meet safety requirements.
