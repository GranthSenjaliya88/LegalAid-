import { useState } from "react";
import { BookOpen, Landmark, SearchX, ScrollText } from "lucide-react";
import type { Domain } from "@/types";
import { useActs, useAuthorities, useCorpusSearch, useCorpusStats } from "@/hooks/useCorpus";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { CardSkeletonGrid, LoadingState } from "@/components/common/LoadingState";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ResourceSearch } from "@/components/resources/ResourceSearch";
import { ResourceFilters } from "@/components/resources/ResourceFilters";
import { ResourceCard } from "@/components/resources/ResourceCard";
import { ActCard } from "@/components/resources/ActCard";
import { AuthorityCard } from "@/components/resources/AuthorityCard";

/**
 * Legal Resources explorer (Part 18). Everything shown here is read from the
 * verified corpus via the backend — search results, Acts, and authority
 * directory rows. No legal content is generated on the client.
 */
export function ResourcesPage() {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [domain, setDomain] = useState<Domain | undefined>(undefined);

  const stats = useCorpusStats();
  const search = useCorpusSearch({ q: submitted, domain, limit: 24 }, submitted.trim().length > 0);
  const acts = useActs();
  const authorities = useAuthorities(domain);

  const results = search.data?.results ?? [];
  const hasSearched = submitted.trim().length > 0;

  const statLine = stats.data
    ? `${stats.data.total_acts} Acts · ${stats.data.total_sections} sections in the verified corpus`
    : "A verified library of Indian legal sources.";

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Legal Resources"
        title="Explore the law behind your rights"
        description={statLine}
      />

      <Tabs defaultValue="search" className="space-y-6">
        <TabsList>
          <TabsTrigger value="search">
            <BookOpen className="size-4" />
            Search
          </TabsTrigger>
          <TabsTrigger value="acts">
            <ScrollText className="size-4" />
            Acts
          </TabsTrigger>
          <TabsTrigger value="authorities">
            <Landmark className="size-4" />
            Authorities
          </TabsTrigger>
        </TabsList>

        {/* Search the corpus */}
        <TabsContent value="search" className="space-y-5">
          <ResourceSearch />
          <ResourceFilters value={domain} onChange={setDomain} />

          {!hasSearched && (
            <EmptyState
              icon={BookOpen}
              title="Search the verified legal corpus"
              description="Look up a law, a section, or a plain-language topic like “security deposit” or “unpaid wages”. Every result links to its official source."
            />
          )}

          {hasSearched && search.isLoading && <LoadingState label="Searching the corpus…" />}

          {hasSearched && search.isError && (
            <ErrorState
              title="Search didn't complete"
              description="Please try again in a moment."
              onRetry={() => search.refetch()}
            />
          )}

          {hasSearched && !search.isLoading && !search.isError && results.length === 0 && (
            <EmptyState
              icon={SearchX}
              title="No matches found"
              description="Try different words, or remove the category filter. You can also describe your situation to the assistant instead."
            />
          )}

          {results.length > 0 && (
            <div className="space-y-4">
              {results.map((match, i) => (
                <ResourceCard key={`${match.act}-${match.section}-${i}`} match={match} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Browse Acts */}
        <TabsContent value="acts" className="space-y-5">
          {acts.isLoading && <CardSkeletonGrid count={6} />}
          {acts.isError && (
            <ErrorState
              title="Couldn't load Acts"
              description="Please try again in a moment."
              onRetry={() => acts.refetch()}
            />
          )}
          {acts.data && acts.data.length === 0 && (
            <EmptyState icon={ScrollText} title="No Acts available yet" description="The corpus is still being populated." />
          )}
          {acts.data && acts.data.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {acts.data.map((act) => (
                <ActCard key={act.id} act={act} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Authority directory */}
        <TabsContent value="authorities" className="space-y-5">
          <ResourceFilters value={domain} onChange={setDomain} />
          {authorities.isLoading && <CardSkeletonGrid count={6} />}
          {authorities.isError && (
            <ErrorState
              title="Couldn't load the directory"
              description="Please try again in a moment."
              onRetry={() => authorities.refetch()}
            />
          )}
          {authorities.data && authorities.data.length === 0 && (
            <EmptyState
              icon={Landmark}
              title="No authorities listed"
              description="There are no directory entries for this category yet."
            />
          )}
          {authorities.data && authorities.data.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {authorities.data.map((authority, i) => (
                <AuthorityCard key={authority.id ?? i} authority={authority} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
