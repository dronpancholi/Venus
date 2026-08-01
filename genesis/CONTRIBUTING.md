# CONTRIBUTING TO GENESIS-I

## How to Add a New Validator

1. Create a file in `genesis/validation/validators/`
2. Subclass `BaseValidator`
3. Implement `validate(self, target)` returning `ValidationResult`
4. Register in `ValidationEngine._register_builtins()`

## How to Add a New Code Generator

1. Create a file in `genesis/compiler/codegen/`
2. Subclass `CodeGenerator`
3. Implement `generate(self, cu, output_dir)` returning `list[Path]`
4. Register in `Compiler.__init__()` via `self.codegen_registry.register()`

## How to Add a New Compiler Pass

1. Create a file in `genesis/compiler/passes/`
2. Subclass `CompilerPass`
3. Implement `run(self, cu)` returning `CompilationUnit`
4. Register in `Compiler.__init__()` via `self.pass_registry.register()`

## Coding Standards

- Type hints on all public methods
- No placeholder content, no TODOs in production code
- Every module has a docstring explaining its purpose
- Tests in `tests/` directory
- Follow existing patterns in neighboring modules

## Review Process

1. All new validators must have tests
2. All new capabilities must be registered in CapabilityRegistry
3. All new entities must extend BaseEntity
4. All new graph operations must export to Neo4j-compatible format
