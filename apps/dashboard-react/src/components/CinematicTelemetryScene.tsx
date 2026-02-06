import { Float } from "@react-three/drei"
import { Canvas, useFrame } from "@react-three/fiber"
import { useMemo, useRef } from "react"
import * as THREE from "three"

interface CinematicTelemetrySceneProps {
  healthScore: number
  cinematicMode: boolean
}

function SignalCloud({
  healthScore,
  cinematicMode,
}: CinematicTelemetrySceneProps) {
  const pointsRef = useRef<THREE.Points>(null)
  const size = 220
  const radius = 1.65
  const confidenceSpread = Math.max(0.2, Math.min(1, healthScore / 100))

  const positions = useMemo(() => {
    const out = new Float32Array(size * 3)
    for (let i = 0; i < size; i++) {
      const angle = i * 0.42
      const y = (Math.sin(i * 0.37) * 0.8 + Math.random() * 0.4 - 0.2) * confidenceSpread
      const radial = radius + Math.sin(i * 0.2) * 0.35
      out[i * 3] = Math.cos(angle) * radial
      out[i * 3 + 1] = y
      out[i * 3 + 2] = Math.sin(angle) * radial
    }
    return out
  }, [confidenceSpread])

  useFrame((_, delta) => {
    if (!pointsRef.current || !cinematicMode) return
    pointsRef.current.rotation.y += delta * 0.16
    pointsRef.current.rotation.x = Math.sin(Date.now() * 0.0002) * 0.12
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#42E5FF"
        size={0.025}
        transparent
        opacity={0.72}
        sizeAttenuation
      />
    </points>
  )
}

function PulseCore({
  healthScore,
  cinematicMode,
}: CinematicTelemetrySceneProps) {
  const mesh = useRef<THREE.Mesh>(null)
  const ring = useRef<THREE.Mesh>(null)
  const intensity = 0.35 + Math.max(0.2, Math.min(1, healthScore / 100)) * 0.9

  useFrame((_, delta) => {
    if (!mesh.current || !ring.current) return
    if (cinematicMode) {
      mesh.current.rotation.y += delta * 0.28
      ring.current.rotation.z += delta * 0.18
      ring.current.rotation.x += delta * 0.08
    }
    const pulse = 1 + Math.sin(Date.now() * 0.002) * 0.08
    mesh.current.scale.setScalar(pulse)
  })

  return (
    <group>
      <mesh ref={mesh}>
        <icosahedronGeometry args={[0.42, 1]} />
        <meshStandardMaterial
          color="#53C8D8"
          emissive="#42E5FF"
          emissiveIntensity={intensity}
          roughness={0.25}
          metalness={0.55}
          wireframe={false}
        />
      </mesh>

      <mesh ref={ring}>
        <torusGeometry args={[0.8, 0.028, 24, 200]} />
        <meshStandardMaterial
          color="#FF8C42"
          emissive="#FF8C42"
          emissiveIntensity={0.55}
          roughness={0.4}
          metalness={0.35}
        />
      </mesh>
    </group>
  )
}

function OrbitLattice({ cinematicMode }: { cinematicMode: boolean }) {
  const lattice = useRef<THREE.Group>(null)

  useFrame((_, delta) => {
    if (!lattice.current || !cinematicMode) return
    lattice.current.rotation.y += delta * 0.08
  })

  return (
    <group ref={lattice}>
      {[
        { radius: 1.2, color: "#42E5FF" },
        { radius: 1.55, color: "#7CF7A5" },
      ].map((layer) => (
        <mesh key={layer.radius} rotation={[Math.PI / 2.8, 0, 0]}>
          <ringGeometry args={[layer.radius - 0.01, layer.radius + 0.01, 96]} />
          <meshBasicMaterial color={layer.color} transparent opacity={0.35} />
        </mesh>
      ))}
    </group>
  )
}

export default function CinematicTelemetryScene({
  healthScore,
  cinematicMode,
}: CinematicTelemetrySceneProps) {
  return (
    <Canvas
      dpr={[1, 1.6]}
      camera={{ position: [0, 0, 3.9], fov: 46 }}
      gl={{ alpha: true, antialias: true }}
    >
      <color attach="background" args={["#000000"]} />
      <ambientLight intensity={0.38} />
      <directionalLight position={[2.2, 3, 4]} intensity={1.25} color="#42E5FF" />
      <pointLight position={[-3, -1, -2]} intensity={0.6} color="#FF8C42" />

      <Float speed={1.25} rotationIntensity={0.2} floatIntensity={0.45}>
        <PulseCore healthScore={healthScore} cinematicMode={cinematicMode} />
      </Float>

      <SignalCloud healthScore={healthScore} cinematicMode={cinematicMode} />
      <OrbitLattice cinematicMode={cinematicMode} />
    </Canvas>
  )
}
