<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('articles', function (Blueprint $table) {
            $table->id('article_id');
            $table->string('code', 100)->unique()->nullable();
            $table->string('title', 255);
            $table->string('slug', 255)->unique();
            $table->longText('content');
            $table->text('preview_content')->nullable();
            $table->boolean('contains_sensitive_content')->default(false);
            $table->unsignedBigInteger('author_id');
            $table->foreign('author_id')->references('user_id')->on('users')->onDelete('cascade');
            $table->foreignId('category_id')->nullable()->constrained('categories', 'category_id')->nullOnDelete();
            $table->string('thumbnail_url', 255)->nullable();
            $table->enum('status', ['draft', 'pending', 'published', 'archived', 'rejected'])->default('draft');
            $table->integer('views')->default(0);
            $table->foreignId('approved_by')->nullable()->constrained('users', 'user_id');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('articles');
    }
};
