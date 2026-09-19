import { Nav } from "@/components/layout/Nav";
import { Footer } from "@/components/layout/Footer";
import { SmoothScroll } from "@/components/layout/SmoothScroll";
import { Hero } from "@/components/sections/Hero";
import { Proof } from "@/components/sections/Proof";
import { Guarantees } from "@/components/sections/Guarantees";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Need } from "@/components/sections/Need";
import { Never } from "@/components/sections/Never";
import { Faq } from "@/components/sections/Faq";
import { FinalCta } from "@/components/sections/FinalCta";

/** Section order only. Everything else lives in the components. */
export default function Page() {
  return (
    <>
      <SmoothScroll />
      <a
        href="#proof"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-full focus:bg-bright focus:px-5 focus:py-3 focus:text-void"
      >
        Skip to content
      </a>
      <Nav />
      <main className="flex-1">
        <Hero />
        <Proof />
        <Guarantees />
        <HowItWorks />
        <Need />
        <Never />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </>
  );
}
