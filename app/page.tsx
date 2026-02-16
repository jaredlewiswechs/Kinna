import Link from "next/link";

const features = [
  {
    href: "/assemble",
    title: "Assemble",
    description: "Decompose words into kinematic vectors and see their geometric properties.",
    gradient: "from-blue-500/10 to-blue-600/5",
    iconColor: "text-blue-500",
  },
  {
    href: "/compare",
    title: "Compare",
    description: "Compute the Distortion Index between two words to measure geometric alignment.",
    gradient: "from-orange-500/10 to-orange-600/5",
    iconColor: "text-orange-500",
  },
  {
    href: "/regime",
    title: "Regime",
    description: "Detect the physical domain of a query and lock the semantic context.",
    gradient: "from-green-500/10 to-green-600/5",
    iconColor: "text-green-500",
  },
  {
    href: "/build",
    title: "Build",
    description: "Generate sentences from geometric intent templates using vector matching.",
    gradient: "from-purple-500/10 to-purple-600/5",
    iconColor: "text-purple-500",
  },
];

export default function HomePage() {
  return (
    <div className="page-enter">
      {/* Hero */}
      <div className="text-center mb-10 sm:mb-14">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent/10 mb-5">
          <span className="text-accent text-3xl font-bold">K</span>
        </div>
        <h1 className="text-[34px] sm:text-[40px] font-bold tracking-tight leading-tight">
          Kinematic
          <br />
          Linguistics
        </h1>
        <p className="text-label-secondary text-[17px] mt-3 max-w-md mx-auto leading-relaxed">
          Language modeled as geometry. Words as mechanical assemblies.
          Meaning from stability.
        </p>
        <p className="text-label-quaternary text-[13px] mt-2">
          KL v1.4 Specification
        </p>
      </div>

      {/* Feature cards */}
      <div className="grid gap-3">
        {features.map((f) => (
          <Link
            key={f.href}
            href={f.href}
            className={`card p-5 bg-gradient-to-br ${f.gradient} hover:shadow-md transition-shadow duration-300`}
          >
            <h2 className={`text-[17px] font-semibold ${f.iconColor}`}>
              {f.title}
            </h2>
            <p className="text-[15px] text-label-secondary mt-1 leading-relaxed">
              {f.description}
            </p>
          </Link>
        ))}
      </div>

      {/* Quick info */}
      <div className="mt-10 grid grid-cols-3 gap-3">
        <div className="card-inset p-4 text-center">
          <p className="text-[22px] font-bold text-accent">26</p>
          <p className="text-[11px] text-label-quaternary mt-0.5">Glyph Vectors</p>
        </div>
        <div className="card-inset p-4 text-center">
          <p className="text-[22px] font-bold text-accent">7</p>
          <p className="text-[11px] text-label-quaternary mt-0.5">Physics Regimes</p>
        </div>
        <div className="card-inset p-4 text-center">
          <p className="text-[22px] font-bold text-accent">3D</p>
          <p className="text-[11px] text-label-quaternary mt-0.5">Vector Space</p>
        </div>
      </div>

      {/* Axis legend */}
      <div className="card p-5 mt-6">
        <h3 className="section-header">Vector Axes</h3>
        <div className="flex flex-col gap-3 mt-3">
          <div className="flex items-start gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-[#007AFF] mt-1 shrink-0" />
            <div>
              <p className="text-[15px] font-medium">Structure</p>
              <p className="text-[13px] text-label-tertiary">Rigidity, containment, framing &mdash; how much the shape holds</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-[#FF9500] mt-1 shrink-0" />
            <div>
              <p className="text-[15px] font-medium">Force</p>
              <p className="text-[13px] text-label-tertiary">Energy, pressure, impact &mdash; how much the shape pushes</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-[#34C759] mt-1 shrink-0" />
            <div>
              <p className="text-[15px] font-medium">Flow</p>
              <p className="text-[13px] text-label-tertiary">Movement, transfer, flexibility &mdash; how much the shape moves</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
