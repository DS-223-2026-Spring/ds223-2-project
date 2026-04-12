import React, { useState } from "react";

export default function AdVisePrototype() {
  const [step, setStep] = useState("landing");

  const uploadedCreatives = [
    {
      name: "Creative A - Product Hero",
      type: "Image",
      predicted: "3.8% CVR",
      score: 91,
      tag: "Winning creative",
      reason: "Strong CTA visibility, clear product focus, and balanced text density.",
    },
    {
      name: "Creative B - Lifestyle Scene",
      type: "Video",
      predicted: "2.9% CVR",
      score: 83,
      tag: "Good alternative",
      reason: "High visual appeal, but weaker CTA placement for a sales-focused campaign.",
    },
    {
      name: "Creative C - Discount Banner",
      type: "Image",
      predicted: "3.1% CVR",
      score: 78,
      tag: "Needs improvement",
      reason: "Offer is visible, but text density is high and branding is less cohesive.",
    },
  ];

  const metrics = [
    { label: "Predicted Conversion Rate", value: "3.8%", sub: "Sales outcome" },
    { label: "Predicted CTR", value: "2.6%", sub: "Traffic estimate" },
    { label: "Predicted Reach Score", value: "74/100", sub: "Awareness potential" },
    { label: "Predicted Lead Rate", value: "4.1%", sub: "Lead potential" },
    { label: "Predicted Engagement Score", value: "81/100", sub: "Interaction likelihood" },
    { label: "Brand Consistency", value: "88/100", sub: "Website alignment" },
  ];

  const recommendations = [
    "Launch with Creative A as the primary asset for this campaign.",
    "Use a 'Buy now' CTA because it aligns best with your selected Sales objective.",
    "Keep the audience warm and mobile-first for stronger conversion potential.",
    "Reduce text density in Creative C to improve readability across placements.",
  ];

  if (step === "landing") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-white">
        <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8">
          <div className="flex items-center justify-between py-4">
            <div>
              <div className="text-2xl font-bold tracking-tight">AdVise</div>
              <div className="text-sm text-slate-300">AI-powered campaign success prediction</div>
            </div>
            <button
              onClick={() => setStep("form")}
              className="rounded-2xl border border-white/20 bg-white/10 px-5 py-2.5 text-sm font-medium backdrop-blur transition hover:bg-white/20"
            >
              Get started
            </button>
          </div>

          <div className="grid flex-1 items-center gap-10 py-10 lg:grid-cols-2">
            <div>
              <div className="mb-4 inline-flex rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-1.5 text-sm text-emerald-200">
                Predict campaign performance before launch
              </div>
              <h1 className="text-5xl font-bold tracking-tight md:text-6xl">AdVise</h1>
              <p className="mt-4 text-2xl font-medium text-slate-200">Predict Before You Launch</p>
              <p className="mt-6 max-w-xl text-base leading-7 text-slate-300">
                Upload your ad creatives, enter campaign metrics, and receive predicted outcomes plus a recommendation for the strongest creative before spending budget.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <button
                  onClick={() => setStep("form")}
                  className="rounded-2xl bg-white px-6 py-3 text-base font-semibold text-slate-900 shadow-lg transition hover:scale-[1.02]"
                >
                  Get started
                </button>
                <button className="rounded-2xl border border-white/20 px-6 py-3 text-base font-semibold text-white/90">
                  See how it works
                </button>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <div className="text-sm text-slate-300">Upload creatives</div>
                <div className="mt-3 text-3xl">🎞️</div>
                <p className="mt-3 text-sm leading-6 text-slate-300">Images and short videos are analyzed for features that influence campaign performance.</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <div className="text-sm text-slate-300">Input campaign metrics</div>
                <div className="mt-3 text-3xl">📊</div>
                <p className="mt-3 text-sm leading-6 text-slate-300">Add budget, platform, audience, CTA, campaign intent, duration, and other core variables.</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur sm:col-span-2">
                <div className="text-sm text-slate-300">Get prediction dashboard</div>
                <div className="mt-3 text-3xl">🏆</div>
                <p className="mt-3 text-sm leading-6 text-slate-300">See predicted metrics and identify the winning creative for your chosen campaign scenario.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === "form") {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <div className="border-b bg-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <div>
              <div className="text-2xl font-bold tracking-tight">AdVise</div>
              <div className="text-sm text-slate-500">Predict Before You Launch</div>
            </div>
            <button
              onClick={() => setStep("landing")}
              className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium"
            >
              Back
            </button>
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Campaign Input</h1>
            <p className="mt-2 text-slate-600">Upload your creatives and fill in the campaign metrics to generate predictions.</p>
          </div>

          <div className="grid gap-6 lg:grid-cols-12">
            <section className="lg:col-span-4">
              <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
                <h2 className="text-xl font-semibold">Image / Video Uploader</h2>
                <p className="mt-1 text-sm text-slate-500">Upload 1–3 images or short videos</p>

                <div className="mt-5 rounded-3xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center">
                  <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-sm">🎞️</div>
                  <p className="text-base font-medium">Drop your files here</p>
                  <p className="mt-1 text-sm text-slate-500">PNG, JPG, MP4, MOV</p>
                  <button className="mt-4 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-medium text-white">Choose Files</button>
                </div>

                <div className="mt-5 space-y-3">
                  {uploadedCreatives.map((item, index) => (
                    <div key={index} className="rounded-2xl border border-slate-200 p-4">
                      <div className="font-medium">{item.name}</div>
                      <div className="text-sm text-slate-500">{item.type}</div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="lg:col-span-8">
              <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
                <div className="mb-5 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold">Campaign Metrics</h2>
                    <p className="mt-1 text-sm text-slate-500">Based on the required fields in the project definition</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {[
                    ["Budget", "$5,000"],
                    ["Product Type", "Skincare"],
                    ["Audience Metrics", "Interest-based targeting"],
                    ["Age Group", "25–34"],
                    ["Region", "Europe"],
                    ["Audience Temperature", "Warm"],
                    ["Device Type", "Mobile"],
                    ["Customer Type", "Returning"],
                    ["Gender", "All"],
                    ["Career", "Professionals"],
                    ["Campaign Intent", "Sales"],
                    ["Platform", "Instagram"],
                    ["Campaign Duration", "14 days"],
                    ["CTA Type", "Buy now"],
                    ["Discount Offered", "15%"],
                    ["Season / Month", "May"],
                  ].map(([label, value]) => (
                    <label key={label} className="block">
                      <div className="mb-2 text-sm font-medium text-slate-700">{label}</div>
                      <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">{value}</div>
                    </label>
                  ))}
                </div>

                <div className="mt-8 flex justify-end">
                  <button
                    onClick={() => setStep("dashboard")}
                    className="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:scale-[1.02]"
                  >
                    Predict
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <div className="text-2xl font-bold tracking-tight">AdVise</div>
            <div className="text-sm text-slate-500">Prediction Results</div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setStep("form")}
              className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium"
            >
              Edit Inputs
            </button>
            <button className="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-medium text-white">Save Report</button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="rounded-3xl bg-gradient-to-br from-slate-900 to-slate-700 p-6 text-white shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="mb-2 text-sm uppercase tracking-[0.2em] text-slate-300">Winning Creative</div>
              <h1 className="text-3xl font-semibold tracking-tight">Creative A is predicted to perform best</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-300">
                For your selected Sales campaign on Instagram, Creative A shows the strongest expected performance across conversion potential, brand consistency, and CTA clarity.
              </p>
            </div>
            <div className="rounded-3xl bg-white/10 px-5 py-4 backdrop-blur">
              <div className="text-xs uppercase tracking-widest text-slate-300">Creative Score</div>
              <div className="mt-1 text-4xl font-bold">91</div>
              <div className="text-sm text-slate-300">Highest predicted fit</div>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {metrics.map((metric) => (
            <div key={metric.label} className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
              <div className="text-sm text-slate-500">{metric.label}</div>
              <div className="mt-2 text-3xl font-bold tracking-tight">{metric.value}</div>
              <div className="mt-1 text-sm text-slate-500">{metric.sub}</div>
            </div>
          ))}
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-5">
          <div className="xl:col-span-3 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="mb-4">
              <h2 className="text-xl font-semibold">Creative Comparison</h2>
              <p className="text-sm text-slate-500">Prediction summary for uploaded creatives</p>
            </div>

            <div className="space-y-4">
              {uploadedCreatives.map((item, index) => (
                <div key={index} className="rounded-2xl border border-slate-200 p-4">
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{item.name}</h3>
                        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{item.tag}</span>
                      </div>
                      <p className="mt-2 text-sm text-slate-600">{item.reason}</p>
                    </div>
                    <div className="min-w-24 rounded-2xl bg-slate-50 px-4 py-3 text-center">
                      <div className="text-xs uppercase tracking-wider text-slate-500">Score</div>
                      <div className="text-2xl font-bold">{item.score}</div>
                      <div className="text-xs text-slate-500">{item.predicted}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="xl:col-span-2 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="mb-4">
              <h2 className="text-xl font-semibold">Recommendation</h2>
              <p className="text-sm text-slate-500">What AdVise suggests before launch</p>
            </div>

            <div className="space-y-3">
              {recommendations.map((item, index) => (
                <div key={index} className="flex gap-3 rounded-2xl bg-slate-50 p-4">
                  <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
                    {index + 1}
                  </div>
                  <p className="text-sm text-slate-700">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
