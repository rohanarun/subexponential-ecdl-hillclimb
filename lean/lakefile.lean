import Lake
open Lake DSL

package ecdl where
  version := v!"0.1.0"

@[default_target]
lean_lib ECDL where
  srcDir := "."
