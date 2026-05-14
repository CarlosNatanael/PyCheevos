### Example 1: Hi
`string_equals(0x1000, "Hi")`
|   # | Flag   | LType   | LSize     | LValue   | Op   | RType   | RSize   | RValue   | Hits   |
|----:|:-------|:--------|:----------|:---------|:-----|:--------|:--------|:---------|:-------|
|   1 |        | Mem     | 16-bit BE | 0x1000   | =    | Value   |         | 0x4869   |        |

### Example 2: Hello World
`string_equals(0x1000, "Hello World")`
|   # | Flag    | LType   | LSize     | LValue   | Op   | RType   | RSize   | RValue     | Hits   |
|----:|:--------|:--------|:----------|:---------|:-----|:--------|:--------|:-----------|:-------|
|   1 | AndNext | Mem     | 32-bit BE | 0x1000   | =    | Value   |         | 0x48656c6c |        |
|   2 | AndNext | Mem     | 32-bit BE | 0x1004   | =    | Value   |         | 0x6f20576f |        |
|   3 |         | Mem     | 24-bit BE | 0x1008   | =    | Value   |         | 0x726c64   |        |

### Example 3: Fixed length
`string_equals(0x1000, "Hello World", 3)`
|   # | Flag   | LType   | LSize     | LValue   | Op   | RType   | RSize   | RValue   | Hits   |
|----:|:-------|:--------|:----------|:---------|:-----|:--------|:--------|:---------|:-------|
|   1 |        | Mem     | 24-bit BE | 0x1000   | =    | Value   |         | 0x48656c |        |

### Example 4: Transform method
`string_equals(0x1000, "Hello World", transform=delta)`
|   # | Flag    | LType   | LSize     | LValue   | Op   | RType   | RSize   | RValue     | Hits   |
|----:|:--------|:--------|:----------|:---------|:-----|:--------|:--------|:-----------|:-------|
|   1 | AndNext | Delta   | 32-bit BE | 0x1000   | =    | Value   |         | 0x48656c6c |        |
|   2 | AndNext | Delta   | 32-bit BE | 0x1004   | =    | Value   |         | 0x6f20576f |        |
|   3 |         | Delta   | 24-bit BE | 0x1008   | =    | Value   |         | 0x726c64   |        |

### Example 5: Little endian
`string_equals(0x1000, "Hello World", endianness="little")`
|   # | Flag    | LType   | LSize   | LValue   | Op   | RType   | RSize   | RValue     | Hits   |
|----:|:--------|:--------|:--------|:---------|:-----|:--------|:--------|:-----------|:-------|
|   1 | AndNext | Mem     | 32-bit  | 0x1000   | =    | Value   |         | 0x6c6c6548 |        |
|   2 | AndNext | Mem     | 32-bit  | 0x1004   | =    | Value   |         | 0x6f57206f |        |
|   3 |         | Mem     | 24-bit  | 0x1008   | =    | Value   |         | 0x646c72   |        |

### Example 6: UTF-16 encoding
`string_equals(0x1000, "Hello World", encoding="utf-16")`
|   # | Flag    | LType   | LSize     | LValue   | Op   | RType   | RSize   | RValue     | Hits   |
|----:|:--------|:--------|:----------|:---------|:-----|:--------|:--------|:-----------|:-------|
|   1 | AndNext | Mem     | 32-bit BE | 0x1000   | =    | Value   |         | 0xfffe4800 |        |
|   2 | AndNext | Mem     | 32-bit BE | 0x1004   | =    | Value   |         | 0x65006c00 |        |
|   3 | AndNext | Mem     | 32-bit BE | 0x1008   | =    | Value   |         | 0x6c006f00 |        |
|   4 | AndNext | Mem     | 32-bit BE | 0x100c   | =    | Value   |         | 0x20005700 |        |
|   5 | AndNext | Mem     | 32-bit BE | 0x1010   | =    | Value   |         | 0x6f007200 |        |
|   6 |         | Mem     | 32-bit BE | 0x1014   | =    | Value   |         | 0x6c006400 |        |

### Example 7: Japanese LE SHIFT-JIS
`string_equals(0x1000, "こんにちは", encoding="shift-jis", endianness="little")`
|   # | Flag    | LType   | LSize   | LValue   | Op   | RType   | RSize   | RValue     | Hits   |
|----:|:--------|:--------|:--------|:---------|:-----|:--------|:--------|:-----------|:-------|
|   1 | AndNext | Mem     | 32-bit  | 0x1000   | =    | Value   |         | 0xf182b182 |        |
|   2 | AndNext | Mem     | 32-bit  | 0x1004   | =    | Value   |         | 0xbf82c982 |        |
|   3 |         | Mem     | 16-bit  | 0x1008   | =    | Value   |         | 0xcd82     |        |

